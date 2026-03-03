"""Helpers that wrap openMINDS boilerplate for dataset ingestion.

Usage:
    from ingestion_helpers import create_dataset, save_datasets

Requires: pip install openMINDS
"""

import json
from pathlib import Path

from openminds import Collection, IRI
import openminds.latest.core as omcore
import openminds.latest.controlled_terms as omterms
import openminds.latest.sands as omsands

# Handle class rename between openMINDS versions
_CoordSpace = getattr(
    omsands,
    "CustomCoordinateFramework",
    getattr(omsands, "CustomCoordinateSpace", None),
)

OUTPUT_DIR = Path(__file__).parent.parent / "dataset_directory" / "data-volumes"


def create_dataset(
    *,
    name,
    description,
    version="1.0",
    license="CC-BY-4.0",
    digital_identifier,
    contributors,
    project_id,
    channel_name,
    measured_quantity,
    studied_target,
    species,
    developmental_stage,
    technique,
    orientation,
    shape,
    voxel_size_um,
    coordinate_space,
    subject_id=None,
    injection_target=None,
    injection_coordinate=None,
    **extra_fields,
):
    """Create a dataset metadata dict and matching openMINDS objects.

    Parameters are plain Python types (strings, lists, dicts) matching
    the fields in proposal/README.md.  Returns ``(metadata_dict,
    openminds_nodes, folder_name)``.

    The dataset folder name is derived from ``name`` and
    ``channel_name`` (e.g. ``"visp_viral_tracing_mouse_7_gfp"``),
    so re-running the script is idempotent.

    Any additional keyword arguments (e.g. ``sample_number``,
    ``number_of_female``) are stored in metadata.json as-is.
    These are fields not represented in openMINDS.
    """
    folder_name = _make_folder_name(name, channel_name)

    # ── plain metadata dict (written to metadata.json) ────────────
    metadata = {
        "name": name,
        "description": description,
        "version": version,
        "license": license,
        "digital_identifier": digital_identifier,
        "contributors": contributors,
        "project_id": project_id,
        "channel_name": channel_name,
        "measured_quantity": measured_quantity,
        "studied_target": studied_target,
        "species": species,
        "developmental_stage": developmental_stage,
        "technique": technique,
        "orientation": orientation,
        "shape": shape,
        "voxel_size_um": voxel_size_um,
        "coordinate_space": coordinate_space,
    }
    if subject_id is not None:
        metadata["subject_id"] = subject_id
    if injection_target is not None:
        metadata["injection_target"] = injection_target
    if injection_coordinate is not None:
        metadata["injection_coordinate"] = injection_coordinate
    # extra (non-openMINDS) fields go straight into the metadata
    metadata.update(extra_fields)

    # ── openMINDS objects ─────────────────────────────────────────
    nodes = []

    if subject_id is not None:
        # single-animal dataset
        subject_state = omcore.SubjectState(
            age_category=_resolve_age_category(developmental_stage),
            internal_identifier=subject_id,
        )
        subject = omcore.Subject(
            internal_identifier=subject_id,
            species=_resolve_species(species),
            studied_states=[subject_state],
        )
        nodes.extend([subject_state, subject])
        specimens = [subject]
    else:
        # population average — use SubjectGroup
        group = omcore.SubjectGroup(
            internal_identifier=folder_name,
            species=_resolve_species(species),
            number_of_subjects=extra_fields.get("sample_number"),
        )
        nodes.append(group)
        specimens = [group]

    coord = _CoordSpace(
        name=coordinate_space,
        anatomical_axes_orientation=_resolve_orientation(orientation),
        native_unit=omterms.UnitOfMeasurement.micrometer,
    )
    repo = omcore.FileRepository(
        iri=IRI(
            f"file://data-volumes/{folder_name}"
            f"/{version.replace('.', '_')}/volume.ome.zarr"
        ),
        name=f"{channel_name} volume",
    )
    ds_version = omcore.DatasetVersion(
        full_name=name,
        short_name=channel_name,
        version_identifier=version,
        version_innovation=f"{channel_name}: {measured_quantity}",
        description=description,
        techniques=_resolve_techniques(technique),
        studied_specimens=specimens,
        repository=repo,
    )

    nodes.extend([coord, repo, ds_version])
    return metadata, nodes, folder_name


def save_datasets(datasets, output_dir=None):
    """Write metadata.json files and a combined openMINDS collection.

    *datasets* is a list of ``(metadata_dict, openminds_nodes,
    folder_name)`` tuples as returned by :func:`create_dataset`.
    """
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR

    for meta, nodes, folder_name in datasets:
        # write metadata.json
        version_dir = meta["version"].replace(".", "_")
        ds_dir = output_dir / folder_name / version_dir
        ds_dir.mkdir(parents=True, exist_ok=True)
        (ds_dir / "volume.ome.zarr").mkdir(exist_ok=True)
        with open(ds_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")

        # save openMINDS JSON-LD next to metadata.json
        collection = Collection()
        for node in nodes:
            collection.add(node)
        jsonld_path = ds_dir / "openminds.jsonld"
        collection.save(str(jsonld_path))
        print(f"Saved {ds_dir}")


# ── private helpers ───────────────────────────────────────────────────

def _make_folder_name(name, channel_name):
    """Derive a deterministic folder name from dataset name.

    If the name doesn't already contain the channel name, it is
    appended.  E.g. "VISp viral tracing - Mouse 7 - GFP"
    -> "visp_viral_tracing_mouse_7_gfp"
    """
    raw = name
    if channel_name.lower() not in name.lower():
        raw = f"{name} {channel_name}"
    parts = (
        raw.lower()
        .replace("-", " ")
        .replace("/", " ")
        .split()
    )
    return "_".join(parts)


def _resolve_species(name):
    lookup = {
        "Mus musculus": omterms.Species.mus_musculus,
    }
    return lookup.get(name, omterms.Species(name=name))


def _resolve_age_category(stage):
    lookup = {
        "adult": omterms.AgeCategory.adult,
        "embryo": omterms.AgeCategory.embryo,
        "juvenile": omterms.AgeCategory.juvenile,
    }
    return lookup.get(stage)


def _resolve_orientation(code):
    lookup = {
        "asr": omterms.AnatomicalAxesOrientation.asr,
    }
    return lookup.get(code)


def _resolve_techniques(techniques):
    lookup = {
        "anterograde tracing": omterms.Technique.anterograde_tracing,
        "light sheet fluorescence microscopy": (
            omterms.Technique.light_sheet_fluorescence_microscopy
        ),
    }
    resolved = []
    for t in techniques:
        if t in lookup:
            resolved.append(lookup[t])
        else:
            resolved.append(omterms.Technique(name=t))
    return resolved
