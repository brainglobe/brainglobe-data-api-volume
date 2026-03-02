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

- each dataset is given a UUID
- volume data stored as zarr
- We use fields from openminds, stored in a json
- Metadata will be stored as a sqlite database so we can query quickly. We will build the database from the jsons.


## Metadata fields

These are not from openMINDS:

* `name` -  dataset name.
* `description` - What the dataset contains.
* `id` - UUID, unique dataset identifier.
* `version` - Semantic version (e.g. `"1.0"`).
* `license` - Usage terms (e.g. `"CC-BY-4.0"`).
* `citation` - Publication reference and DOI.
* `contributors` - Labs or authors who produced the data.

## Scientific Fields (openMINDS-derived)

* `species` -  species name (e.g. "Mus musculus") - I guess this should follow the brainglobe atlas api since each dataset should have a corresponding CCF in the atlas api
* `biological_sex` - Female, male, hermaphrodite, not detectable.
* `developmental_stage` - Life cycle class: adolescent, adult, embryo, infant, juvenile, etc.
* `injection_target` - Injection target regions, nested with the annotation set they belong to: `{regions, annotation_set: {name, version}}`.
* `injection_coordinate` - Specific coordinate in the related coordinate space (e.g. `[6600, 4000, 5400]`).
* `technique` - Method of accomplishing a desired aim. 194 valid values from openMINDS.
* `measured_quantity` - What the voxel values represent (e.g. fluorescence intensity, cell density).

## Spatial Fields

* `orientation` - BrainGlobe orientation code (e.g. `"asr"`).
* `shape` - Volume dimensions in voxels.
* `voxel_size_um` - Voxel size in micrometers.
* `coordinate_space` - The BrainGlobe coordinate space the data is registered to, as `{name, version}`.

## Volume Fields

* `volume.format` - Data format (e.g. `"ome-zarr"`).
* `volume.multiscale` - Whether the volume has multiple resolution levels.
* `volume.path` - Relative path to the volume file within the dataset directory.
* `volume.channels` - Per-channel metadata: `[{index, name, measured_quantity}, ...]`. Multi-channel data uses OME-Zarr's built-in channel support; this array describes what each channel represents.
