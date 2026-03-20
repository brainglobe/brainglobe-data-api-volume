from brainglobe_data_api_volume import query_arrays, BrainGlobeArray

# 1. Query the local metadata index (SQLite)
#
# We can query using openMINDS-derived metadata fields.
# See proposal/metadata/README.md for supported fields.

results = query_arrays(
    technique="viral tracing",
    injection_target="MOp",
    species="Mus musculus",
)

# Returns a DataFrame with columns: id, name, species, technique, ...
target_array_id = results.iloc[0]["id"]

# 2. Load the array (downloads volume to local cache if not present)
array = BrainGlobeArray(target_array_id)

# 3. Access the volume data (numpy array)
intensity_map = array.values  # shape: (132, 80, 114)

# 4. Access metadata
print(array.metadata.species)  # "Mus musculus"
print(array.metadata.voxel_size_um)  # [100.0, 100.0, 100.0]
print(array.metadata.coordinate_space) # The coordinate space the array is registered to
project_id = array.metadata.project_id
arrays_from_project = query_arrays(project = project_id)
print(arrays_from_project)
