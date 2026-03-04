"""Population average c-Fos activity map (single channel, no subject_id)."""

import random
import uuid

from ingestion_helpers import create_array, save_arrays

rng = random.Random(42)

PROJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))

cfos = create_array(
    name="Whole-brain c-Fos population average",
    description="Average c-Fos expression map from 12 adult mice "
    "after novel environment exposure",
    digital_identifier="https://doi.org/10.9999/cfos-avg",
    contributors=["Lee Lab, Francis Crick Institute"],
    project_id=PROJECT_ID,
    project_name="Whole-brain c-Fos activity mapping",
    project_description="Population average c-Fos expression after "
    "novel environment exposure in adult mice",
    channel_name="c-Fos",
    measured_quantity="cell density",
    studied_target="c-Fos",
    species="Mus musculus",
    developmental_stage="adult",
    technique=[
        "immunostaining",
        "light sheet fluorescence microscopy",
    ],
    orientation="asr",
    shape=[528, 320, 456],
    voxel_size_um=[25.0, 25.0, 25.0],
    coordinate_space="allen_mouse",
    # ── population average fields (not in openMINDS) ──────────
    sample_number=12,
    number_of_female=6,
    number_of_male=6,
    number_of_hermaphrodite=0,
    age=90,
    age_units="days",
)

save_arrays([cfos])
