"""Template script for generating a BrainGlobe atlas.

Use this script as a starting point to package a new BrainGlobe atlas by
filling in the required functions and metadata.
"""

from pathlib import Path

import pooch
from brainglobe_utils.IO.image import load_any

from brainglobe_data_api_volume.atlas_generation.wrapup import (
    wrapup_volume_from_data,
)

# Copy-paste this script into a new file and fill in the functions to package
# your own atlas.

### Metadata ###

# The minor version of the atlas in the brainglobe_atlasapi, this is internal,
# if this is the first time this atlas has been added the value should be 0
# (minor version is the first number after the decimal point, ie the minor
# version of 1.2 is 2)
__version__ = 0

# The expected format is FirstAuthor_SpeciesCommonName, e.g. kleven_rat, or
# Institution_SpeciesCommonName, e.g. allen_mouse.
# remember to add {ATLAS_NAME}_{RESOLUTION}um to:
# brainglobe_atlasapi/atlas_names.py
ATLAS_NAME = "carey_interactive_gene_mouse"

# BrainGlobe atlas the gene volumes are registered to.
ATLAS_SPACE = "carea_mouse_25um"

# DOI of the most relevant citable document
CITATION = "https://doi.org/10.64898/2026.01.20.700446"

# The scientific name of the species, ie; Rattus norvegicus
SPECIES = "mus musculus"

# The URL for the data files
ATLAS_LINK = (
    "https://data-proxy-zipper.ebrains.eu/zip?container="
    "https%3A%2F%2Fdata-proxy.ebrains.eu%2Fapi%2Fv1%2Fdatasets%2F"
    "7f8ef0e2-121a-4892-8a5e-1c7a8b693503%3Fprefix%3Dgene_volumes%2F"
)

# The orientation of the **original** atlas data, in BrainGlobe convention:
# https://brainglobe.info/documentation/setting-up/image-definition.html#orientation
ORIENTATION = "asr"

# The id of the highest level of the atlas. This is commonly called root or
# brain. Include some information on what to do if your atlas is not
# hierarchical
ROOT_ID = None

# The resolution of your volume in microns. Details on how to format this
# parameter for non isotropic datasets or datasets with multiple resolutions.
RESOLUTION = 25

BG_ROOT_DIR = Path.home() / "brainglobe_workingdir" / ATLAS_NAME

# Package one gene while validating. Change the name to test another gene,
# or set to None to package all genes.
GENE_TO_PACKAGE = "Rorb"


def download_resources() -> list[Path]:
    """Download and extract the gene volume datasets into ``BG_ROOT_DIR``.

    The archive is cached as ``gene_volumes.zip`` and its contents are
    extracted into ``gene_volumes/``, preserving the archive's directory
    structure. Downloading and extraction are skipped if that directory
    already contains files.

    Returns
    -------
    list[pathlib.Path]
        Paths to the extracted dataset files.
    """
    existing_files = [
        file for file in (BG_ROOT_DIR / "gene_volumes").rglob("*")
    ]
    print("existing files: ", len(existing_files))
    if len(existing_files) == 4083:
        return

    pooch.retrieve(
        url=ATLAS_LINK,
        # No checksum is supplied for this archive.
        known_hash=None,
        fname="gene_volumes.zip",
        path=BG_ROOT_DIR,
        processor=pooch.Unzip(extract_dir="gene_volumes"),
        progressbar=True,
    )


def retrieve_reference_and_annotation():
    """
    Retrieve the reference and annotation volumes.

    If possible, use brainglobe_utils.IO.image.load_any for opening images.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        A tuple containing the reference volume and the annotation volume.
    """
    reference = None
    annotation = None
    return reference, annotation


def retrieve_hemisphere_map():
    """
    Retrieve a hemisphere map for the atlas.

    Use a hemisphere map if the atlas is asymmetrical. This map is an array
    with the same shape as the template, where 1 marks the left hemisphere
    and 2 marks the right.

    Returns
    -------
    np.ndarray or None
        A numpy array representing the hemisphere map, or None if the atlas
        is symmetrical.
    """
    return None


def retrieve_structure_information():
    """
    Return a list of dictionaries with information about the atlas.

    Returns a list of dictionaries, where each dictionary represents a
    structure and contains its ID, name, acronym, hierarchical path,
    and RGB triplet.

    The expected format for each dictionary is:

    .. code-block:: python

        {
            "id": int,
            "name": str,
            "acronym": str,
            "structure_id_path": list[int],
            "rgb_triplet": list[int, int, int],
        }

    Returns
    -------
    list[dict]
        A list of dictionaries, each containing information for a single
        atlas structure.
    """
    return None


def retrieve_or_construct_meshes():
    """
    Return a dictionary mapping structure IDs to paths of mesh files.

    If the atlas is packaged with mesh files, download and use them. Otherwise,
    construct the meshes using available helper functions.

    Returns
    -------
    dict
        A dictionary where keys are structure IDs and values are paths to the
        corresponding mesh files.
    """
    meshes_dict = {}
    return meshes_dict


def retrieve_volumes(gene: str | None = None):
    """Load cached NIfTI volumes, named by their source gene filenames.

    If gene is provided, load only that gene (for example, "Sst").
    Source names are preserved; no Ensembl ID mapping is applied.
    """
    source_dir = BG_ROOT_DIR / "gene_volumes"
    existing_files = sorted(source_dir.rglob("*.nii.gz"))
    if gene is not None:
        existing_files = [
            file
            for file in existing_files
            if file.name.removesuffix(".nii.gz") == gene
        ]
        if not existing_files:
            raise FileNotFoundError(f"No cached volume for {gene!r}")
    volumes = {}
    for file in existing_files:
        reference_name = file.name.removesuffix(".nii.gz")
        if reference_name in volumes:
            raise ValueError(f"Duplicate gene volume: {reference_name}")
        volumes[reference_name] = load_any(file, as_numpy=True)
    return volumes


### If the code above this line has been filled correctly, nothing needs to be
### edited below (unless variables need to be passed between the functions).
if __name__ == "__main__":
    if RESOLUTION is None:
        raise ValueError("RESOLUTION must be set before running this script.")

    bg_root_dir = BG_ROOT_DIR
    bg_root_dir.mkdir(parents=True, exist_ok=True)

    download_resources()
    reference_volume, annotated_volume = retrieve_reference_and_annotation()
    volumes = retrieve_volumes(GENE_TO_PACKAGE)
    hemispheres_stack = retrieve_hemisphere_map()
    structures = retrieve_structure_information()
    meshes_dict = retrieve_or_construct_meshes()

    output_paths = wrapup_volume_from_data(
        atlas_name=ATLAS_NAME,
        atlas_space=ATLAS_SPACE,
        atlas_minor_version=__version__,
        citation=CITATION,
        atlas_link=ATLAS_LINK,
        species=SPECIES,
        resolution=(RESOLUTION,) * 3,
        orientation=ORIENTATION,
        root_id=ROOT_ID,
        reference_stack=reference_volume,
        annotation_stack=annotated_volume,
        structures_list=structures,
        meshes_dict=meshes_dict,
        working_dir=bg_root_dir,
        hemispheres_stack=None,
        volumes=volumes,
        overwrite=True,
    )

    for output_path in output_paths:
        print(f"Saved: {output_path}")
