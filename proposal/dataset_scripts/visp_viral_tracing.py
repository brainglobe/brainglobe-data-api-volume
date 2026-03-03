"""VISp viral tracing - Mouse 7 (GFP + autofluorescence channels)."""

import random
import uuid

from ingestion_helpers import create_dataset, save_datasets

rng = random.Random(7)
SUBJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))
PROJECT_ID = str(uuid.UUID(int=rng.getrandbits(128), version=4))

COMMON = dict(
    version="1.0",
    license="CC-BY-4.0",
    citation="Smith et al 2025, https://doi.org/10.1234/visp-tracing",
    contributors=["Smith Lab, Sainsbury Wellcome Centre"],
    subject_id=SUBJECT_ID,
    project_id=PROJECT_ID,
    species="Mus musculus",
    developmental_stage="adult",
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

gfp = create_dataset(
    name="VISp viral tracing - Mouse 7 - GFP",
    description="AAV-GFP anterograde tracing from primary visual cortex "
    "(GFP channel)",
    channel_name="GFP",
    measured_quantity="fluorescence intensity",
    studied_target="GFP",
    **COMMON,
)

autofluo = create_dataset(
    name="VISp viral tracing - Mouse 7 - autofluorescence",
    description="AAV-GFP anterograde tracing from primary visual cortex "
    "(autofluorescence channel)",
    channel_name="autofluorescence",
    measured_quantity="fluorescence intensity",
    studied_target="autofluorescence",
    **COMMON,
)

save_datasets([gfp, autofluo])
