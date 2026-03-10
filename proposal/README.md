# Implementation of data api proposal

Based on the atlas API v2. This document provides a broad overview of the data API.

* basic_usage.py shows what it will look like to actually use the API.
* array_scripts shows a mock ingestion.
* array_directory shows how the volumes will be stored

## Directory Structure

```text
array_directory/
├── projects/
│   └── <project_id>.json
├── subjects/
│   └── <subject_id>.json           # only for individual animals
└── arrays/
    └── visp_viral_tracing_mouse_7_gfp/
        └── 1_0/
            ├── metadata.json
            ├── openminds.jsonld
            └── volume.ome.zarr/
```

### Notes

- each array is given a UUID (`id` field in metadata.json)
- volume data stored as OME-Zarr
- We use fields from openMINDS, stored in JSON
- An openMINDS JSON-LD file is generated alongside each array for interoperability
- Metadata will be stored as a SQLite database so we can query quickly. We will build the database from the JSONs.
- Projects and subjects are separate entities, linked by ID to avoid duplication


## Three Entities

The schema has three entity types. **Projects** and **subjects** are
defined once and referenced by ID from each **array**.

### Project (required fields)
* `project_id` - UUID identifying the project.
* `name` - Human-readable project name (e.g. `"VISp viral tracing"`).
* `description` - Brief description of the project's aims.
* `digital_identifier` - DOI for the associated publication (e.g. `"https://doi.org/10.1234/example"`).
* `contributors` - Labs or authors who produced the data.

### Subject (required fields)
* `species` - Species name (e.g. `"Mus musculus"`). Should correspond to a BrainGlobe atlas species.
* `developmental_stage` - Life cycle class: adolescent, adult, embryo, infant, juvenile, etc.
* `sample_number` - Number of animals (1 for an individual, >1 for a population average).
* `number_of_male` - Number of male animals.
* `number_of_female` - Number of female animals.
* `number_of_hermaphrodite` - Number of hermaphrodite animals.

#### Subject (optional fields)
* `subject_id` - UUID identifying an individual animal. Present for single-animal arrays, absent for population averages. All arrays derived from the same animal share this ID, allowing multi-channel data to be linked.
* `strain` - Mouse strain or line (e.g. `"C57BL/6J"`, `"Drd1a-Cre"`).
* `age` - Age at time of imaging (or average age for population averages).
* `age_units` - Units for interpreting the `age` field (e.g. `"days"`, `"weeks"`).

### Array (required fields)
* `id` - UUID, unique array identifier (generated deterministically from the folder name and version).
* `name` - Array name.
* `description` - What the array contains.
* `version` - Semantic version (e.g. `"1.0"`).
* `license` - Usage terms (e.g. `"CC-BY-4.0"`).
* `project_id` - Reference to the project this array belongs to.
* `channel_name` - Human-readable name for this channel (e.g. `"GFP"`, `"tdTomato"`, `"autofluorescence"`).
* `measured_quantity` - What the voxel values represent (e.g. fluorescence intensity, cell density). Since each channel is its own array, this is always a single quantity.
* `studied_target` - What were we trying to measure (e.g. DRD1, c-Fos, Nissl).
* `technique` - Method of accomplishing a desired aim. 194 valid values from openMINDS.
* `orientation` - BrainGlobe orientation code (e.g. `"asr"`).
* `shape` - Volume dimensions in voxels.
* `voxel_size_um` - Voxel size in micrometers.
* `coordinate_space` - The BrainGlobe atlas name the data is registered to (e.g. `"allen_mouse"`). Must be a valid atlas in `brainglobe_atlasapi`. Resolution is not included here — it is captured by `voxel_size_um`.

#### Array (optional fields)
* `subject_id` - Reference to the subject (present for individual animals).
* `studied_gene` - Dictionary with gene metadata for the studied target: `{gene_name, gene_description, synonyms, ensembl_id}`.
* `injection_target` - Injection target regions, nested with the annotation set they belong to: `{regions, annotation_set: {name, version}}`. The `name` is a BrainGlobe atlas name (e.g. `"allen_mouse"`).
* `injection_coordinate` - Specific coordinate in the related coordinate space (e.g. `[5700, 2800, 3600]`).


## Channel Splitting

Each channel of a multi-channel volume is stored as a **separate array** with its own UUID and metadata. This means:

- A single-channel acquisition produces one array.
- A multi-channel acquisition (e.g. two fluorescence channels) produces one array per channel.
- Related channels can be linked via a shared `subject_id` (animal UUID) so they can be grouped back together when needed.

This keeps each array simple (one volume = one measured quantity) and avoids the complexity of per-channel metadata arrays.

## Population Averages

An individual animal is treated as a population average where n=1. This keeps the schema uniform:

- Individual: `sample_number=1`, `number_of_male=1`, `number_of_female=0`, etc.
- Population: `sample_number=12`, `number_of_male=6`, `number_of_female=6`, etc.

Population averages have no `subject_id` (there is no single animal to reference). Their subject metadata is embedded directly in the array metadata.json rather than stored as a separate file.
