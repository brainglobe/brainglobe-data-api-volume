# Implementation of data api proposal

Based on the atlas API v2.

## Dataset Structure

```text
proposal/example_dataset/
└── data-volumes/
    └── 550e8400-e29b-41d4-a716-446655440000/
        └── 1_0/
            ├── metadata.json
            └── volume.ome.zarr/
                └── .placeholder
```

### Notes

- Each dataset is given a UUID.
- Volume data stored as OME-Zarr (multi-channel data uses OME-Zarr's built-in channel support).
- A single `metadata.json` per dataset version contains both technical and scientific metadata.
- Scientific metadata fields are sourced from openMINDS, modified where needed, and stored as JSON for simplicity.
- Version format: dots in metadata (`"1.0"`), underscores in directory names (`1_0/`).

## Metadata

See [metadata/README.md](metadata/README.md) for the full list of supported fields.

Key fields include:
- **Catalogue fields**: `name`, `description`, `license`, `citation`, `contributors`
- **Scientific fields** (openMINDS-derived): `species`, `biological_sex`, `developmental_stage`, `injection_target`, `injection_coordinate`, `technique`, `measured_quantity`
- **Spatial fields**: `orientation`, `shape`, `voxel_size_um`, `coordinate_space`
- **Volume info**: `format`, `multiscale`, `path`

The `injection_target` field nests the target regions with the annotation set they belong to, since region acronyms are only meaningful within a specific annotation set. The `injection_coordinate` stores the CCF coordinate in the related coordinate space.

The `coordinate_space` field stores `{name, version}` to identify the BrainGlobe atlas. Storage paths are resolved at runtime by the atlas API.

## Database

- Metadata is queryable via a local **SQLite** database, managed by the package.
- The database is built from the `metadata.json` files.
- Future: sqlite-vec extension for vector similarity search.
- `query_datasets()` runs queries against this local database and returns a DataFrame.

## Query & Access Flow

1. On first use / periodically, the metadata index is synced locally.
2. `query_datasets()` queries the local SQLite database.
3. `BrainGlobeDataset(id)` downloads the volume data to a local cache on first access.
4. `dataset.values` returns the volume as a numpy array.
5. `dataset.get_atlas()` returns the matching BrainGlobeAtlas for the coordinate space.

See [basic_usage.py](basic_usage.py) for a complete example.
