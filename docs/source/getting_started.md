# Getting started

Gene volumes packaged by `packaging_scripts`
can be loaded as a named dataset through the public API:

```python
from pathlib import Path
from brainglobe_data_api_volume import BrainGlobeVolume

dataset = BrainGlobeVolume(
    "carey_interactive_gene_mouse_25um",
    brainglobe_dir=(
        Path.home() / "brainglobe_workingdir" / "carey_interactive_gene_mouse"
    ),
    check_latest=False,
)

print(list(dataset.volumes))
rorb = dataset.volumes["rorb"]
print(rorb.shape)
```

`brainglobe_dir` is the parent of the `brainglobe-data-api` output directory.
Omit it when the dataset is in your configured BrainGlobe directory.
`check_latest=False` skips online version checks for this local dataset.

The wrapup writes a manifest under
`brainglobe-data-api/manifests/carey_interactive_gene_mouse_25um/<version>/`
and the gene volumes under `brainglobe-data-api/volumes/`. The manifest lists
which volumes belong to the dataset. Volume arrays load on first access.
The packaging script converts names to ASCII and lowercases them at discovery:
`Rórb.nii.gz` becomes `rorb`. Wrapup requires lowercase ASCII names and uses
them unchanged for volume directories and lookup keys.
Normalization uses Python's standard library for accents, full-width letters,
and Unicode dashes. Other non-ASCII characters are rejected.


Pass `atlas_space="allen_mouse_25um"` to `wrapup_volume_from_data` to record the
BrainGlobe atlas the dataset is registered to. Read it from
`dataset.metadata["atlas_space"]` after loading the dataset.

This dataset contains volumes only. Template, annotation,
hemisphere, and hierarchy properties are unavailable. Complete atlas packages
continue to expose those properties.

## View a volume in napari

Then load `dataset` and `rorb` using the example above. In a standalone Python
script, display the volume in pixel coordinates with:

```python
import napari

viewer = napari.Viewer()
viewer.add_image(rorb, name="Rorb", colormap="magma")
napari.run()
```

Arrays use voxel indices, as in `brainglobe_atlasapi`. Voxel size is recorded
separately in `dataset.resolution` and the OME-Zarr scale metadata.

In Jupyter or IPython, enable the Qt event loop with `%gui qt` after the
graphics setup, then create the viewer and add the image as above. Omit
`napari.run()` in that case.
