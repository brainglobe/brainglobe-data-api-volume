from brainglobe_data_api_volume import query_datasets, BrainGlobeDataset

# 1. Query the local metadata index (SQLite)
#
# We can query using openMINDS-derived metadata fields.
# See proposal/metadata/README.md for supported fields.

results = query_datasets(
    technique="viral tracing",
    injection_target="MOp",
    species="Mus musculus",
)

# Returns a DataFrame with columns: id, name, species, technique, ...
target_dataset_id = results.iloc[0]["id"]

# 2. Load the dataset (downloads volume to local cache if not present)
dataset = BrainGlobeDataset(target_dataset_id)

# 3. Access the volume data (numpy array)
intensity_map = dataset.values  # shape: (132, 80, 114)

# 4. Access metadata
print(dataset.metadata.species)  # "Mus musculus"
print(dataset.metadata.voxel_size_um)  # [100.0, 100.0, 100.0]

# 5. Get the matching atlas (if brainglobe-atlasapi is installed)
atlas = dataset.get_atlas()  # returns BrainGlobeAtlas for the coordinate space
