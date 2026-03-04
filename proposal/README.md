# Implementation of data api proposal

Based on the atlas API v2. This document provides a broad overview of the data API.

* basic_usage.py shows what it will look like to actually use the API.
* array_scripts shows a mock ingestion.
* array_directory shows how the volumes will be stored

## Array Structure

```text
proposal/example_dataset/
└── data-volumes/
    ├── 550e8400-e29b-41d4-a716-446655440000/   # GFP channel
    │   └── 1_0/
    │       ├── metadata.json
    │       └── volume.ome.zarr/
    │           └── .placeholder
    └── 660e8400-e29b-41d4-a716-446655440001/   # autofluorescence channel
        └── 1_0/
            ├── metadata.json
            └── volume.ome.zarr/
                └── .placeholder
```
### Notes

- each array is given a UUID
- volume data stored as zarr
- We use fields from openminds, stored in a json
- Metadata will be stored as a sqlite database so we can query quickly. We will build the database from the jsons.


## Metadata fields

These are not from openMINDS (or I couldnt find them):

* `id` - UUID, unique array identifier.
* `injection_coordinate` - Specific coordinate in the related coordinate space (e.g. `[6600, 4000, 5400]`).

## openMINDS-derived fields
* `name` -  array name.
* `contributors` - Labs or authors who produced the data.
* `description` - What the array contains.
* `dataset_version` - Semantic version (e.g. `"1.0"`).
* `license` - Usage terms (e.g. `"CC-BY-4.0"`).
* `species` -  species name (e.g. "Mus musculus") - I guess this should follow the brainglobe atlas api since each array should have a corresponding CCF in the atlas api
* `developmental_stage` - Life cycle class: adolescent, adult, embryo, infant, juvenile, etc.
* `injection_target` - Injection target regions, nested with the annotation set they belong to: `{regions, annotation_set: {name, version}}`. The `name` is a BrainGlobe atlas name (e.g. `"allen_mouse"`).
* `technique` - Method of accomplishing a desired aim. 194 valid values from openMINDS.
* `measured_quantity` - What the voxel values represent (e.g. fluorescence intensity, cell density). Since each channel is its own array, this is always a single quantity.
* `studied_target` - What were we trying to measure (e.g. DRD1, C-Fos, Nissl )
* `digital_identifier` - DOI for the associated publication (e.g. `"10.1234/example"`).
* `anatomical_axes_orientation` - BrainGlobe orientation code (e.g. `"asr"`).
* `voxel_size_um` - Voxel size in micrometers.
* `coordinate_space` - The BrainGlobe atlas name the data is registered to (e.g. `"allen_mouse"`). Must be a valid atlas in `brainglobe_atlasapi`. Resolution is not included here — it is captured by `voxel_size_um`.
* `shape` - Volume dimensions in voxels.

## my fields for handling population average datasets
* `sample_number` -  number of animals used to create this average.
* `number_of_female` -  the number of female animals used to create this average.
* `number_of_male` -  the number of male animals used to create this average.
* `number_of_hemaphrodite` -  the number of hemaprodite animals used to create this average.
* `age` -  The average age of animals used in this dataset
* `age_units` -  the units for interpreting the age variable



## Channel Splitting

Each channel of a multi-channel volume is stored as a **separate array** with its own UUID and metadata. This means:

- A single-channel acquisition produces one array.
- A multi-channel acquisition (e.g. two fluorescence channels) produces one array per channel.
- Related channels can be linked via a shared `subject_id` (animal UUID) so they can be grouped back together when needed.

This keeps each array simple (one volume = one measured quantity) and avoids the complexity of per-channel metadata arrays.

## Project Metadata

* `project_id` - UUID identifying the project this array belongs to. Arrays produced as part of the same set (e.g. a study or publication) share this ID.
* `project_name` - Human-readable project name (e.g. `"VISp viral tracing"`).
* `project_description` - Brief description of the project's aims.

## Subject (Animal) Metadata

* `subject_id` - UUID identifying the animal (subject) the data came from. All arrays derived from the same animal share this ID, allowing multi-channel or multi-modal data to be linked. An individual animal is treated as a population average where n=1.
* `strain` - Mouse strain or line (e.g. `"C57BL/6J"`, `"Drd1a-Cre"`).
* `age` - Age at time of imaging (or average age for population averages).
* `age_units` - Units for interpreting the `age` field (e.g. `"days"`, `"weeks"`).

## Channel Metadata

* `channel_name` - Human-readable name for this channel (e.g. `"GFP"`, `"tdTomato"`, `"autofluorescence"`).
