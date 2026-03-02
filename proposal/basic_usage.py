from brainglobe_data_api import query_datasets, BrainGlobeDataset
from brainglobe_atlasapi import BrainGlobeAtlas
# 1. Discover the dataset using openMINDS metadata

"""
we can query using openminds metadata. Relevant fields we might start with are
mentioned in our supported-metadata.md file.

"""
results = query_datasets(
    technique="viral tracing",
    anatomical_target="MOp")

#returns a dataframe with matching datasets and the associated metadata
target_dataset_name = results.iloc[0]["unique_name"]

# 2. Load the dataset (downloads manifest, prepares Zarr connection)
dataset = BrainGlobeDataset(target_dataset_name)

# 3. Load the array values
intensity_map = dataset.values

# optional. Retrieve the associated BrainGlobeAtlas
# not clear how we will be able to access atlases via
# common_coordinate_spaces yet in bg-atlasv2
atlas_name = dataset.common_coordinate_space # -> allen_mouse
dataset_resolution = dataset.volume_resolution_um
atlas = BrainGlobeAtlas(f"{atlas_name}_{dataset_resolution}_um")



