# Getting started

Gene volumes packaged by `packaging_scripts`
can be loaded as a named dataset through the public API:

```python
from pathlib import Path
from brainglobe_data_api_volume import BrainGlobeAtlas

atlas = BrainGlobeAtlas(
    "carey_interactive_gene_mouse_25um",
    brainglobe_dir=(
        Path.home() / "brainglobe_workingdir" / "carey_interactive_gene_mouse"
    ),
    check_latest=False,
)

print(list(atlas.additional_references))
rorb = atlas.additional_references["rorb"]
print(rorb.shape)
```

`brainglobe_dir` is the parent of the `brainglobe-atlasapi` output directory.
Omit it when the dataset is in your configured BrainGlobe directory.
`check_latest=False` skips online version checks for this local dataset.

The wrapup writes a manifest under
`brainglobe-atlasapi/atlases/carey_interactive_gene_mouse_25um/<version>/`
and the gene volumes under `brainglobe-atlasapi/templates/`. The manifest lists
which references belong to the dataset. Reference aryrays load on first access.
Reference keys are lowercase gene names, such as `rorb` and `sst`.

Pass `atlas_space="allen_mouse_25um"` to `wrapup_atlas_from_data` to record the
BrainGlobe atlas the dataset is registered to. Read it from
`atlas.metadata["atlas_space"]` after loading the dataset.

This dataset contains additional references only. Template, annotation,
hemisphere, and hierarchy properties are unavailable. Complete atlas packages
continue to expose those properties.

## View a volume in napari

Then load `atlas` and `rorb` using the example above. In a standalone Python
script, display the volume in pixel coordinates with:

```python
import napari

viewer = napari.Viewer()
viewer.add_image(rorb, name="Rorb", colormap="magma")
napari.run()
```

Arrays use voxel indices, as in `brainglobe_atlasapi`. Voxel size is recorded
separately in `atlas.resolution` and the OME-Zarr scale metadata.

In Jupyter or IPython, enable the Qt event loop with `%gui qt` after the
graphics setup, then create the viewer and add the image as above. Omit
`napari.run()` in that case.
