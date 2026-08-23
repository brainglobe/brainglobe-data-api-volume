"""VISp viral tracing - Mouse 7 (GFP + autofluorescence channels)."""

import random
import uuid

from ingestion_helpers import create_project, create_subject, create_array, save_arrays

rng = random.Random(7)
SUBJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))
PROJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))

project = create_project(
    project_id=PROJECT_ID,
    name="VISp viral tracing",
    description="Anterograde tracing from primary visual cortex "
    "using AAV-GFP in adult mice",
    digital_identifier="https://doi.org/10.1234/visp-tracing",
    contributors=["Smith Lab, Sainsbury Wellcome Centre"],
)

subject = create_subject(
    subject_id=[SUBJECT_ID],
    species="Mus musculus",
    developmental_stage="adult",
    strain=["C57BL/6J"],
    sample_number=1,
    biological_sex=["male"],
    age=[90],
    age_units=["days"],
)

COMMON = dict(
    project=project,
    subject=subject,
    technique=[
        "anterograde tracing",
        "light sheet fluorescence microscopy",
    ],
    orientation="asr",
    shape=[264, 160, 228],
    voxel_size_um=[50.0, 50.0, 50.0],
    coordinate_space="allen_mouse",
    injection_target={
        "regions": ["VISp"],
        "annotation_set": {
            "name": "allen_mouse",
            "version": "2017",
        },
    },
    injection_coordinate=[5700, 2800, 3600],
)

gfp = create_array(
    name="VISp viral tracing - Mouse 7 - GFP",
    description="AAV-GFP anterograde tracing from primary visual cortex "
    "(GFP channel)",
    channel_name="GFP",
    measured_quantity="fluorescence intensity",
    studied_target="GFP",
    **COMMON,
)

autofluo = create_array(
    name="VISp viral tracing - Mouse 7 - autofluorescence",
    description="AAV-GFP anterograde tracing from primary visual cortex "
    "(autofluorescence channel)",
    channel_name="autofluorescence",
    measured_quantity="fluorescence intensity",
    studied_target="autofluorescence",
    **COMMON,
)

save_arrays([gfp, autofluo], projects=[project], subjects=[subject])
