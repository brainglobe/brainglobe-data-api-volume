"""Whole-brain DRD1 immunostaining - Mouse 13 (single channel)."""

import random
import uuid

from ingestion_helpers import create_dataset, save_datasets

rng = random.Random(13)

drd1 = create_dataset(
    name="Whole-brain DRD1 expression - Mouse 13",
    description="Light sheet fluorescence microscopy of DRD1 "
    "immunostaining across the whole brain",
    citation="Jones et al 2026, https://doi.org/10.5678/drd1-lsfm",
    contributors=["Jones Lab, UCL"],
    subject_id=str(uuid.UUID(int=rng.getrandbits(128), version=4)),
    project_id=str(uuid.UUID(int=rng.getrandbits(128), version=4)),
    channel_name="DRD1",
    measured_quantity="fluorescence intensity",
    studied_target="DRD1",
    species="Mus musculus",
    developmental_stage="adult",
    technique=[
        "immunostaining",
        "light sheet fluorescence microscopy",
    ],
    orientation="asr",
    shape=[528, 320, 456],
    voxel_size_um=[25.0, 25.0, 25.0],
    coordinate_space={
        "name": "allen-adult-mouse-ccf-space",
        "version": "2015",
    },
)

save_datasets([drd1])
