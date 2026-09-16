"""Module containing the core Volume class."""

import shutil
import warnings
from collections import UserDict
from pathlib import Path
from typing import (
    Dict,
    List,
    Tuple,
)

import ngff_zarr as nz
import numpy as np
import s3fs
from brainglobe_space import AnatomicalSpace
from fsspec.callbacks import TqdmCallback

from brainglobe_atlasapi.descriptors import (
    ATLAS_ORIENTATION,
    V3_TEMPLATE_NAME,
)
from brainglobe_atlasapi.utils import read_json

from brainglobe_data_api_volume.descriptors import remote_url_data_s3


def _determine_pyramid_level(
    multiscale: nz.Multiscales, resolution: Tuple[float, float, float]
) -> int:
    """Return the pyramid level matching ``resolution``.

    The scale of each level is read from ``NgffImage.scale``, which ngff-zarr
    populates from the coordinate transformations of the corresponding
    dataset. That mapping is keyed by dimension name and is the same whatever
    OME-Zarr version the store is written in, so it avoids interpreting the
    version-specific transformation metadata directly.

    ``images`` and ``metadata.datasets`` are built in the same pass over the
    stored datasets, so their indices refer to the same pyramid level.

    Parameters
    ----------
    multiscale : nz.Multiscales
        The multiscale image to search.
    resolution : tuple of float
        Requested resolution in microns, in ``(z, y, x)`` order.

    Returns
    -------
    int
        Index of the matching pyramid level.

    Raises
    ------
    ValueError
        If no pyramid level has the requested resolution.
    """
    for idx, image in enumerate(multiscale.images):
        # Only check spatial scale against resolution
        scales = [image.scale[dim] for dim in image.dims[-3:]]
        if all(
            np.isclose(res / 1000, scale)
            for res, scale in zip(resolution, scales)
        ):
            return idx

    raise ValueError(f"Requested resolution {resolution} um is invalid.")


class Volume:
    """Base class to handle volume datasets in BrainGlobe.

    Every dataset served by this API consists solely of volumes registered
    to an atlas space; the atlas components themselves (template, annotation,
    terminology and meshes) are provided by brainglobe-atlasapi.

    Parameters
    ----------
    path : str or Path object
        Path to the manifest.json file describing the dataset.
    """

    def __init__(self, path):
        manifest_path = Path(path)
        self.root_dir = manifest_path.parents[3]
        self.metadata = read_json(manifest_path)

        self.volumes = VolumeDict(
            volumes_list=self.metadata["volumes"],
            data_path=self.root_dir,
            resolution=self.resolution,
        )

        # Instantiate SpaceConvention object describing the current dataset:
        self.space = AnatomicalSpace(
            origin=self.orientation,
            shape=self.shape,
            resolution=self.resolution,
        )

    @property
    def resolution(self):
        """Make resolution more accessible from class."""
        return tuple(self.metadata["resolution"])

    @property
    def orientation(self):
        """Make orientation more accessible from class."""
        return ATLAS_ORIENTATION

    @property
    def shape(self):
        """Make shape more accessible from class."""
        return tuple(self.metadata["shape"])

    @property
    def shape_um(self):
        """Make shape more accessible from class."""
        return tuple([s * r for s, r in zip(self.shape, self.resolution)])


class VolumeDict(UserDict):
    """Class implementing the lazy loading of volumes
    if the dictionary is queried for it.
    """

    def __init__(
        self,
        volumes_list: List[Dict[str, str]],
        data_path,
        resolution: Tuple[float, float, float],
        *args,
        **kwargs,
    ):
        self.data_path = data_path
        self.volume_names = [ref["name"] for ref in volumes_list]
        self.volumes_dict = {ref["name"]: ref for ref in volumes_list}
        self.resolution = resolution
        self.fs = s3fs.S3FileSystem(anon=True)

        super().__init__(*args, **kwargs)

        for volume_name in self.volume_names:
            self.data[volume_name] = None

    def __getitem__(self, key):
        """Retrieve an item from the dictionary using the volume name
        as key.

        If the volume image data for `volume_name` has not been loaded yet,
        it will be read from the disk and cached. If `volume_name` is not
        one of the predefined volumes, a warning is issued
        and None is returned.

        Parameters
        ----------
        key : str
            The name of the volume image to retrieve (e.g., "aba").

        Returns
        -------
        np.ndarray or None
            The image data associated with the volume name, or None if the
            volume name is not found in the list of available volumes.

        Raises
        ------
            KeyError: If the volume_name is not found.
        """
        if key not in self.volume_names:
            warnings.warn(
                f"No volume named {key} "
                f"(available: {self.volume_names})"
            )
            return None

        if self.data[key] is None:
            volume_data = self.volumes_dict.get(key, key)

            volume_location = volume_data["location"][1:]
            local_path: Path = (
                self.data_path / volume_location / V3_TEMPLATE_NAME
            )

            if not local_path.exists():
                print(f"Downloading metadata for volume {key}:")
                remote_metadata_path = remote_url_data_s3.format(
                    f"{volume_location}/{V3_TEMPLATE_NAME}/**/*.json"
                )
                try:
                    self.fs.get(
                        remote_metadata_path,
                        local_path,
                        callback=TqdmCallback(),
                    )
                except BaseException:
                    # Drop a partial download so the next access retries
                    # rather than reading incomplete metadata.
                    shutil.rmtree(local_path, ignore_errors=True)
                    raise

            multiscale = nz.from_ngff_zarr(local_path)
            pyramid_level = _determine_pyramid_level(
                multiscale, self.resolution
            )

            dataset_path = multiscale.metadata.datasets[pyramid_level].path
            resolution_path = local_path / dataset_path

            if not (resolution_path / "c").exists():
                print("Downloading volume...")
                remote_path = remote_url_data_s3.format(
                    f"{volume_location}/{V3_TEMPLATE_NAME}/{dataset_path}/"
                )
                self.fs.get(
                    remote_path,
                    resolution_path,
                    recursive=True,
                    callback=TqdmCallback(),
                )
            self.data[key] = multiscale.images[pyramid_level].data.compute()

        return self.data[key]
