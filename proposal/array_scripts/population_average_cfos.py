"""Population average c-Fos activity map (single channel, no subject_id)."""

import random
import uuid

from ingestion_helpers import create_project, create_subject, create_array, save_arrays

rng = random.Random(42)
PROJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))

project = create_project(
    project_id=PROJECT_ID,
    name="Whole-brain c-Fos activity mapping",
    description="Population average c-Fos expression after "
    "novel environment exposure in adult mice",
    digital_identifier="https://doi.org/10.9999/cfos-avg",
    contributors=["Lee Lab, Francis Crick Institute"],
)

subject = create_subject(
    species="Mus musculus",
    developmental_stage="adult",
    sample_number=12,
    biological_sex=["male"] * 6 + ["female"] * 6,
    strain=["C57BL/6J"] * 12,
    age=[90] * 12,
    age_units=["days"] * 12,
)

cfos = create_array(
    name="Whole-brain c-Fos population average",
    description="Average c-Fos expression map from 12 adult mice "
    "after novel environment exposure",
    project=project,
    subject=subject,
    channel_name="c-Fos",
    measured_quantity="cell density",
    studied_target="c-Fos",
    studied_gene={
        "gene_name": "Fos",
        "gene_description": "FBJ osteosarcoma oncogene",
        "synonyms": ["c-Fos", "AP-1"],
        "ensembl_id": "ENSMUSG00000021250",
    },
    studied_cell_type={
        "name": "neuron",
        "ontology_identifier": "CL:0000540",
        "description": "Electrically excitable cell specialized for synaptic communication.",
    },
    technique=[
        "immunostaining",
        "light sheet fluorescence microscopy",
    ],
    orientation="asr",
    shape=[528, 320, 456],
    voxel_size_um=[25.0, 25.0, 25.0],
    coordinate_space="allen_mouse",
)

save_arrays([cfos], projects=[project])
