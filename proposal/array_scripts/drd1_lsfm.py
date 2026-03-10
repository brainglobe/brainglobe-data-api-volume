"""Whole-brain DRD1 immunostaining - Mouse 13 (single channel)."""

import random
import uuid

from ingestion_helpers import create_project, create_subject, create_array, save_arrays

rng = random.Random(13)
PROJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))
SUBJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))

project = create_project(
    project_id=PROJECT_ID,
    name="Whole-brain DRD1 expression",
    description="Mapping DRD1 expression across the whole brain "
    "using immunostaining and light sheet microscopy",
    digital_identifier="https://doi.org/10.5678/drd1-lsfm",
    contributors=["Jones Lab, UCL"],
)

subject = create_subject(
    subject_id=SUBJECT_ID,
    species="Mus musculus",
    developmental_stage="adult",
    strain="Drd1a-Cre",
    sample_number=1,
    number_of_female=1,
    number_of_male=0,
    number_of_hermaphrodite=0,
    age=120,
    age_units="days",
)

drd1 = create_array(
    name="Whole-brain DRD1 expression - Mouse 13",
    description="Light sheet fluorescence microscopy of DRD1 "
    "immunostaining across the whole brain",
    project=project,
    subject=subject,
    channel_name="DRD1",
    measured_quantity="fluorescence intensity",
    studied_target="DRD1",
    studied_gene={
        "gene_name": "Drd1",
        "gene_description": "Dopamine receptor D1",
        "synonyms": ["D1", "D1R"],
        "ensembl_id": "ENSMUSG00000021478",
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

save_arrays([drd1], projects=[project], subjects=[subject])
