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

These are not from openMINDS (or I couldnt find them):

* `id` - UUID, unique dataset identifier.
* `injection_coordinate` - Specific coordinate in the related coordinate space (e.g. `[6600, 4000, 5400]`).

## openMINDS-derived fields
* `name` -  dataset name.
* `contributors` - Labs or authors who produced the data.
* `description` - What the dataset contains.
* `dataset_version` - Semantic version (e.g. `"1.0"`).
* `license` - Usage terms (e.g. `"CC-BY-4.0"`).
* `species` -  species name (e.g. "Mus musculus") - I guess this should follow the brainglobe atlas api since each dataset should have a corresponding CCF in the atlas api
* `biological_sex` - Female, male, hermaphrodite, not detectable.
* `developmental_stage` - Life cycle class: adolescent, adult, embryo, infant, juvenile, etc.
* `injection_target` - Injection target regions, nested with the annotation set they belong to: `{regions, annotation_set: {name, version}}`.
* `technique` - Method of accomplishing a desired aim. 194 valid values from openMINDS.
* `measured_quantity` - What the voxel values represent (e.g. fluorescence intensity, cell density). Since each channel is its own dataset, this is always a single quantity.
* `digital_identifier` - Publication reference and DOI.
* `anatomical_axes_orientation` - BrainGlobe orientation code (e.g. `"asr"`).
* `voxel_size_um` - Voxel size in micrometers.
* `coordinate_space` - The BrainGlobe coordinate space the data is registered to, as `{name, version}`.
* `shape` - Volume dimensions in voxels.

## my fields for handling population average datasets
* `sample_number` -  number of animals used to create this average.
* `number_of_female` -  the number of female animals used to create this average.
* `number_of_male` -  the number of male animals used to create this average.
* `number_of_hemaphrodite` -  the number of hemaprodite animals used to create this average.
* `age` -  The average age of animals used in this dataset
* `age_units` -  the units for interpreting the age variable



## Channel Splitting

Each channel of a multi-channel volume is stored as a **separate dataset** with its own UUID and metadata. This means:

- A single-channel acquisition produces one dataset.
- A multi-channel acquisition (e.g. two fluorescence channels) produces one dataset per channel.
- Related channels can be linked via a shared `subject_id` (animal UUID) so they can be grouped back together when needed.

This keeps each dataset simple (one volume = one measured quantity) and avoids the complexity of per-channel metadata arrays.

## Additional Metadata Fields for Channel Linking

* `subject_id` - UUID identifying the animal (subject) the data came from. All datasets derived from the same animal share this ID, allowing multi-channel or multi-modal data to be linked.
* `project_id` - UUID identifying the project this dataset belongs to. Datasets produced as part of the same set (e.g. a study or publication) share this ID.
* `channel_name` - Human-readable name for this channel (e.g. `"GFP"`, `"tdTomato"`, `"autofluorescence"`).

## Volume Fields

* `volume.format` - Data format (e.g. `"ome-zarr"`).
* `volume.multiscale` - Whether the volume has multiple resolution levels.
* `volume.path` - Relative path to the volume file within the dataset directory.
