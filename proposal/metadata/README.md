Full metadata details from the openminds fields we are starting with are in [./metadata.md](./metadata.md).

## Catalogue Fields

These are not from openMINDS but are essential for any data catalogue:

* `name` - Human-readable dataset name.
* `description` - What the dataset contains.
* `id` - UUID, unique dataset identifier.
* `version` - Semantic version (e.g. `"1.0"`).
* `license` - Usage terms (e.g. `"CC-BY-4.0"`).
* `citation` - Publication reference and DOI.
* `contributors` - Labs or authors who produced the data.

## Scientific Fields (openMINDS-derived)

* `species` - Binomial species name (e.g. "Mus musculus"). 26 valid values from openMINDS.
* `biological_sex` - Female, male, hermaphrodite, not detectable.
* `developmental_stage` - Life cycle class: adolescent, adult, embryo, infant, juvenile, etc.
* `injection_target` - Injection target regions, nested with the annotation set they belong to: `{regions, annotation_set: {name, version}}`.
* `injection_coordinate` - Specific coordinate in the related coordinate space (e.g. `[6600, 4000, 5400]`).
* `technique` - Method of accomplishing a desired aim. 194 valid values from openMINDS.
* `measured_quantity` - What the voxel values represent (e.g. fluorescence intensity, cell density). Custom controlled vocabulary for volumetric data.

## Spatial Fields

* `orientation` - BrainGlobe orientation code (e.g. `"asr"`).
* `shape` - Volume dimensions in voxels.
* `voxel_size_um` - Voxel size in micrometers.
* `coordinate_space` - The BrainGlobe atlas the data is registered to, as `{name, version}`.

## Volume Fields

* `volume.format` - Data format (e.g. `"ome-zarr"`).
* `volume.multiscale` - Whether the volume has multiple resolution levels.
* `volume.path` - Relative path to the volume file within the dataset directory.
