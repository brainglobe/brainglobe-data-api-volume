"""Volume exports must not modify primary atlas components."""

import json

import ngff_zarr as nz
import numpy as np
import pytest
from brainglobe_atlasapi import descriptors

from brainglobe_data_api_volume import BrainGlobeVolume
from brainglobe_data_api_volume.atlas_generation import atlas_packaging_data
from brainglobe_data_api_volume.atlas_generation import wrapup as wu


@pytest.fixture
def export_args(tmp_path):
    reference = np.arange(64, dtype=np.uint16).reshape(4, 4, 4)
    return dict(
        atlas_name="test_mouse",
        atlas_space="allen_mouse_25um",
        atlas_minor_version=0,
        citation="unpublished",
        atlas_link="",
        species="Mus musculus",
        resolution=[(25, 25, 25), (50, 50, 50)],
        orientation=descriptors.ATLAS_ORIENTATION,
        root_id=1,
        reference_stack=[reference, reference[::2, ::2, ::2]],
        annotation_stack=[
            np.ones((4, 4, 4), dtype=np.uint32),
            np.ones((2, 2, 2), dtype=np.uint32),
        ],
        structures_list=[
            dict(
                id=1,
                name="root",
                acronym="root",
                structure_id_path=[1],
                rgb_triplet=[255, 255, 255],
            )
        ],
        meshes_dict={},
        working_dir=tmp_path,
        volumes={
            "gene": [reference + 1, reference[::2, ::2, ::2] + 1],
        },
    )


def test_only_volumes_are_written(export_args):
    paths = wu.wrapup_volume_from_data(**export_args)
    assert len(paths) == 1
    multiscale = nz.from_ngff_zarr(paths[0])
    for image, expected, resolution in zip(
        multiscale.images,
        export_args["volumes"]["gene"],
        export_args["resolution"],
        strict=True,
    ):
        np.testing.assert_array_equal(image.data.compute(), expected)
        assert tuple(image.scale.values()) == tuple(
            r / 1000 for r in resolution
        )
    output_root = export_args["working_dir"] / "brainglobe-atlasapi"
    assert set(output_root.iterdir()) == {
        output_root / descriptors.V3_TEMPLATE_ROOTDIR,
        output_root / descriptors.V3_ATLAS_ROOTDIR,
    }
    assert [p.name for p in paths[0].parents[1].parent.iterdir()] == [
        "test_mouse-gene-template"
    ]


@pytest.mark.parametrize("overwrite", [False, True])
def test_existing_primary_components_are_untouched(export_args, overwrite):
    root = export_args["working_dir"] / "brainglobe-atlasapi"
    version = f"{wu.ATLAS_VERSION}.0".replace(".", "_")
    component_paths = [
        (descriptors.V3_TEMPLATE_ROOTDIR, "test_mouse-template"),
        (atlas_packaging_data.AnnotationInfo.root_dir, "test_mouse-annotation"),
        (
            atlas_packaging_data.TerminologyInfo.root_dir,
            "test_mouse-terminology",
        ),
        (atlas_packaging_data.CoordinateSpaceInfo.root_dir, "test_mouse-space"),
        (descriptors.V3_ATLAS_ROOTDIR, "test_mouse_25um"),
    ]
    sentinels = []
    for component_root, name in component_paths:
        sentinel = root / component_root / name / version / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep")
        sentinels.append(sentinel)

    paths = wu.wrapup_volume_from_data(**export_args, overwrite=overwrite)
    for sentinel in sentinels:
        assert sentinel.read_text() == "keep"
    assert paths[0].exists()

    if overwrite:
        stale = paths[0].parent / "stale"
        stale.write_text("remove")
        assert (
            wu.wrapup_volume_from_data(**export_args, overwrite=True) == paths
        )
        assert not stale.exists()
    else:
        with pytest.raises(FileExistsError):
            wu.wrapup_volume_from_data(**export_args)


def test_primary_components_are_not_fetched(export_args, monkeypatch):
    requested = []
    monkeypatch.setattr(
        atlas_packaging_data,
        "check_requested_component",
        lambda info, _: requested.append(info.name),
    )
    for key in (
        "template_info",
        "annotation_info",
        "terminology_info",
        "coordinate_space_info",
    ):
        export_args[key] = dict(
            name=key,
            version="1.0",
            use_existing=True,
        )
    wu.wrapup_volume_from_data(**export_args)
    assert requested == ["test_mouse-gene-template"]


def test_empty_export_writes_nothing(export_args):
    export_args["volumes"] = {}
    assert wu.wrapup_volume_from_data(**export_args) == []
    assert not (export_args["working_dir"] / "brainglobe-atlasapi").exists()


@pytest.mark.parametrize("legacy_manifest", [False, True])
def test_volume_api_round_trip(export_args, legacy_manifest):
    wu.wrapup_volume_from_data(**export_args)
    manifests = list(export_args["working_dir"].rglob("manifest.json"))
    assert len(manifests) == len(export_args["resolution"])
    for path in manifests:
        metadata = json.loads(path.read_text())
        assert metadata["volumes_only"] is True
        assert [volume["name"] for volume in metadata["volumes"]] == ["gene"]
        assert "additional_references" not in metadata
        if legacy_manifest:
            metadata["additional_references"] = metadata.pop("volumes")
            metadata["additional_references_only"] = metadata.pop(
                "volumes_only"
            )
            path.write_text(json.dumps(metadata))
    for resolution, expected in zip(
        export_args["resolution"], export_args["volumes"]["gene"], strict=True
    ):
        dataset = BrainGlobeVolume(
            f"test_mouse_{resolution[0]}um",
            brainglobe_dir=export_args["working_dir"],
            check_latest=False,
        )
        assert dataset.metadata["atlas_space"] == export_args["atlas_space"]
        assert dataset.resolution == resolution
        assert list(dataset.volumes) == ["gene"]
        assert dataset.volumes.data["gene"] is None
        np.testing.assert_array_equal(dataset.volumes["gene"], expected)
        assert dataset.volumes["gene"] is dataset.volumes.data["gene"]
        with pytest.raises(AttributeError, match="only volumes"):
            _ = dataset.template
