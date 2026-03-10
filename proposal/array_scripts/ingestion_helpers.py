"""Helpers that wrap openMINDS boilerplate for array ingestion.

Usage:
    from ingestion_helpers import (
        create_project, create_subject, create_array, save_arrays,
    )

Requires: pip install openMINDS
"""

import json
import uuid as _uuid
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

OUTPUT_DIR = Path(__file__).parent.parent / "array_directory" / "arrays"

# Namespace UUID for deterministic array ID generation
_NS_ARRAY = _uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def create_project(
    *,
    project_id,
    name,
    description,
    digital_identifier,
    contributors,
):
    """Create a project metadata dict.

    Returns a plain dict that can be passed to :func:`create_array`
    and is saved to ``projects/<project_id>.json`` by :func:`save_arrays`.
    """
    return {
        "project_id": project_id,
        "name": name,
        "description": description,
        "digital_identifier": digital_identifier,
        "contributors": contributors,
    }


def create_subject(
    *,
    species,
    developmental_stage,
    sample_number=1,
    number_of_male=0,
    number_of_female=0,
    number_of_hermaphrodite=0,
    subject_id=None,
    strain=None,
    age=None,
    age_units=None,
):
    """Create a subject metadata dict.

    For individual animals set ``subject_id`` and ``sample_number=1``.
    For population averages omit ``subject_id`` and set
    ``sample_number`` to the cohort size.

    Returns a plain dict that can be passed to :func:`create_array`.
    Subjects with a ``subject_id`` are saved to
    ``subjects/<subject_id>.json`` by :func:`save_arrays`.
    """
    meta = {
        "species": species,
        "developmental_stage": developmental_stage,
        "sample_number": sample_number,
        "number_of_male": number_of_male,
        "number_of_female": number_of_female,
        "number_of_hermaphrodite": number_of_hermaphrodite,
    }
    if subject_id is not None:
        meta["subject_id"] = subject_id
    if strain is not None:
        meta["strain"] = strain
    if age is not None:
        meta["age"] = age
    if age_units is not None:
        meta["age_units"] = age_units
    return meta


def create_array(
    *,
    name,
    description,
    project,
    subject,
    channel_name,
    measured_quantity,
    studied_target,
    technique,
    orientation,
    shape,
    voxel_size_um,
    coordinate_space,
    version="1.0",
    license="CC-BY-4.0",
    studied_gene=None,
    studied_cell_type=None,
    injection_target=None,
    injection_coordinate=None,
    **extra_fields,
):
    """Create an array metadata dict and matching openMINDS objects.

    Parameters are plain Python types (strings, lists, dicts) matching
    the fields in proposal/README.md.  ``project`` and ``subject`` are
    dicts returned by :func:`create_project` and :func:`create_subject`.

    Returns ``(metadata_dict, openminds_nodes, folder_name)``.

    The array folder name is derived from ``name`` and
    ``channel_name`` (e.g. ``"visp_viral_tracing_mouse_7_gfp"``),
    so re-running the script is idempotent.

    Any additional keyword arguments are stored in metadata.json as-is.
    """
    folder_name = _make_folder_name(name, channel_name)

    # deterministic UUID from folder name + version
    array_id = str(_uuid.uuid5(_NS_ARRAY, f"{folder_name}/{version}"))

    # ── plain metadata dict (written to metadata.json) ────────────
    metadata = {
        "id": array_id,
        "name": name,
        "description": description,
        "version": version,
        "license": license,
        "project_id": project["project_id"],
        "channel_name": channel_name,
        "measured_quantity": measured_quantity,
        "studied_target": studied_target,
        "technique": technique,
        "orientation": orientation,
        "shape": shape,
        "voxel_size_um": voxel_size_um,
        "coordinate_space": coordinate_space,
    }
    if subject.get("subject_id") is not None:
        metadata["subject_id"] = subject["subject_id"]
    else:
        # population average — embed subject fields in array metadata
        metadata.update(subject)
    if studied_gene is not None:
        metadata["studied_gene"] = _validate_studied_gene(studied_gene)
    if studied_cell_type is not None:
        metadata["studied_cell_type"] = _validate_studied_cell_type(studied_cell_type)
    if injection_target is not None:
        metadata["injection_target"] = injection_target
    if injection_coordinate is not None:
        metadata["injection_coordinate"] = injection_coordinate
    metadata.update(extra_fields)

    # ── openMINDS objects ─────────────────────────────────────────
    species = subject["species"]
    developmental_stage = subject["developmental_stage"]
    nodes = []

    if subject.get("subject_id") is not None:
        # single-animal array
        state_kwargs = {
            "age_category": _resolve_age_category(developmental_stage),
            "internal_identifier": subject["subject_id"],
        }
        if subject.get("age") is not None:
            state_kwargs["age"] = omcore.QuantitativeValue(
                value=subject["age"],
                unit=_resolve_unit(subject["age_units"])
                if subject.get("age_units")
                else None,
            )
        subject_state = omcore.SubjectState(**state_kwargs)
        om_subject = omcore.Subject(
            internal_identifier=subject["subject_id"],
            species=_resolve_species(species),
            studied_states=[subject_state],
        )
        nodes.extend([subject_state, om_subject])
        specimens = [om_subject]
    else:
        # population average — use SubjectGroup
        group = omcore.SubjectGroup(
            internal_identifier=folder_name,
            species=_resolve_species(species),
            number_of_subjects=subject.get("sample_number"),
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
            f"file://arrays/{folder_name}"
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


def save_arrays(arrays, projects, subjects=None, output_dir=None):
    """Write array, project, and subject metadata files.

    *arrays* is a list of ``(metadata_dict, openminds_nodes,
    folder_name)`` tuples as returned by :func:`create_array`.

    *projects* is a list of project dicts from :func:`create_project`.

    *subjects* is an optional list of subject dicts (with
    ``subject_id``) from :func:`create_subject`.
    """
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR

    # ── save project files ─────────────────────────────────────────
    projects_dir = output_dir.parent / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    for proj in projects:
        path = projects_dir / f"{proj['project_id']}.json"
        with open(path, "w") as f:
            json.dump(proj, f, indent=2)
            f.write("\n")
        print(f"Saved project {path}")

    # ── save subject files ─────────────────────────────────────────
    if subjects:
        subjects_dir = output_dir.parent / "subjects"
        subjects_dir.mkdir(parents=True, exist_ok=True)
        for subj in subjects:
            if subj.get("subject_id") is None:
                continue
            path = subjects_dir / f"{subj['subject_id']}.json"
            with open(path, "w") as f:
                json.dump(subj, f, indent=2)
                f.write("\n")
            print(f"Saved subject {path}")

    # ── save array files ───────────────────────────────────────────
    for meta, nodes, folder_name in arrays:
        version_dir = meta["version"].replace(".", "_")
        arr_dir = output_dir / folder_name / version_dir
        arr_dir.mkdir(parents=True, exist_ok=True)
        (arr_dir / "volume.ome.zarr").mkdir(exist_ok=True)
        with open(arr_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")

        collection = Collection()
        for node in nodes:
            collection.add(node)
        collection.save(str(arr_dir / "openminds.jsonld"))
        print(f"Saved array  {arr_dir}")


# ── private helpers ───────────────────────────────────────────────────

def _make_folder_name(name, channel_name):
    """Derive a deterministic folder name from array name.

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


def _validate_studied_gene(studied_gene):
    required_keys = {
        "gene_name",
        "gene_description",
        "synonyms",
        "ensembl_id",
    }
    if not isinstance(studied_gene, dict):
        raise TypeError("studied_gene must be a dict")

    missing = required_keys - set(studied_gene.keys())
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"studied_gene is missing required keys: {missing_list}")

    if not isinstance(studied_gene["gene_name"], str):
        raise TypeError("studied_gene['gene_name'] must be a string")
    if not isinstance(studied_gene["gene_description"], str):
        raise TypeError("studied_gene['gene_description'] must be a string")
    if not isinstance(studied_gene["synonyms"], list) or not all(
        isinstance(s, str) for s in studied_gene["synonyms"]
    ):
        raise TypeError("studied_gene['synonyms'] must be a list of strings")
    if not isinstance(studied_gene["ensembl_id"], str):
        raise TypeError("studied_gene['ensembl_id'] must be a string")

    return {
        "gene_name": studied_gene["gene_name"],
        "gene_description": studied_gene["gene_description"],
        "synonyms": studied_gene["synonyms"],
        "ensembl_id": studied_gene["ensembl_id"],
    }


def _validate_studied_cell_type(studied_cell_type):
    if not isinstance(studied_cell_type, dict):
        raise TypeError("studied_cell_type must be a dict")

    if "name" not in studied_cell_type:
        raise ValueError("studied_cell_type is missing required key: name")
    if not isinstance(studied_cell_type["name"], str):
        raise TypeError("studied_cell_type['name'] must be a string")

    optional_keys = {"ontology_identifier", "description", "definition"}
    allowed_keys = {"name", *optional_keys}
    unknown_keys = set(studied_cell_type.keys()) - allowed_keys
    if unknown_keys:
        unknown_list = ", ".join(sorted(unknown_keys))
        raise ValueError(
            "studied_cell_type contains unsupported keys: "
            f"{unknown_list}"
        )

    normalized = {"name": studied_cell_type["name"]}
    for key in optional_keys:
        if key in studied_cell_type:
            if not isinstance(studied_cell_type[key], str):
                raise TypeError(f"studied_cell_type['{key}'] must be a string")
            normalized[key] = studied_cell_type[key]

    return normalized


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


def _resolve_unit(unit):
    lookup = {
        "days": omterms.UnitOfMeasurement.day,
        "weeks": omterms.UnitOfMeasurement.week,
        "months": omterms.UnitOfMeasurement.month,
        "years": omterms.UnitOfMeasurement.year,
    }
    return lookup.get(unit, omterms.UnitOfMeasurement(name=unit))


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
