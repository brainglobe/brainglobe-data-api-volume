"""Volume exports must not modify primary atlas components."""

import json

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


def _read_manifest(export_args):
    path = wu._volume_manifest_path(
        export_args["working_dir"] / "brainglobe-data-api",
        export_args["atlas_name"],
        f"{wu.ATLAS_VERSION}.0",
        export_args["resolution"][0],
    )
    return json.loads(path.read_text())


def test_alternate_names_are_written_to_manifest(export_args):
    wu.wrapup_volume_from_data(
        **export_args, alternate_names={"gene": ["Gene", "Gn1"]}
    )
    assert _read_manifest(export_args)["alternate_names"] == {
        "gene": ["Gene", "Gn1"]
    }


def test_alternate_names_default_to_empty(export_args):
    wu.wrapup_volume_from_data(**export_args)
    assert _read_manifest(export_args)["alternate_names"] == {}


@pytest.mark.parametrize(
    "alternate_names",
    [{"missing": ["Missing"]}, {"gene": "Gene"}, {"gene": [1]}],
)
def test_invalid_alternate_names_are_rejected(export_args, alternate_names):
    with pytest.raises(ValueError, match="alternate_names"):
        wu.wrapup_volume_from_data(
            **export_args, alternate_names=alternate_names
        )
    assert not (export_args["working_dir"] / "brainglobe-data-api").exists()


def test_empty_export_writes_nothing(export_args):
    export_args["volumes"] = {}
    assert wu.wrapup_volume_from_data(**export_args) == []
    assert not (export_args["working_dir"] / "brainglobe-data-api").exists()

