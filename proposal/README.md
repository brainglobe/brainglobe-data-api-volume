# Implementation of data api proposal 

Based on the atlas API v2. 

## Dataset Structure

```text
proposal/example_dataset/
└── data-volumes/
    └── 550e8400-e29b-41d4-a716-446655440000/
        └── 1_0/
            ├── manifest.json
            ├── metadata.json
            └── volume.ome.zarr/
                └── .placeholder
```
### Notes

- each dataset is given a UUID
- volume data stored as zarr
- Two metadata files one is the manifest and a seperate one for openminds / scientific metadata.
- We use fields from openminds, modify them where we need and store them in a json for simplicity. 
- Metadata will be stored as a postgres database so we can query quickly. We will build the database from the jsons. 



