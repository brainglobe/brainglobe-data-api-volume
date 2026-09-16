# brainglobe-data-api-volume

The BrainGlobe Data API for Volumes provides a common interface for downloading and interacting with 3D atlas registered volumes. 

## Datasets available


| Dataset Name | Resolution | Ages | content | Name in API  |
| --- |  --- | --- | --- | --- |
|interactive 3D atlas of gene expression in the mouse brain | 25 micron | P56 |  gene expression | carey_interactive_gene_mouse_25um |


## Installation

### Python API 

## List datasets
To see a list of datasets use brainglobe_data_api_volume.show_datasets
```python
from brainglobe_data_api_volume import show_datasets
show_datasets()
```
```python
╭──────────────────────────────── BrainGlobe Datasets ─────────────────────────────────╮
│                                                                           Latest     │
│  Name                              Downloaded  Updated  Local version    version     │
│  carey_interactive_gene_mouse_25…      ✔          ✔          3.0           3.0       │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

## Using the datasets

All the features can be accessed via the BrainGlobeVolume class
```python
from brainglobe_data_api_volume import BrainGlobeVolume
dataset = BrainGlobeVolume("carey_interactive_gene_mouse_25um")
```
The volumes associated with this dataset can then be accessed via the `volume` attribute

```python
volumes = list(dataset.volumes)
print(volumes[-5:])
# ['znrf1', 'zscan22', 'zswim6', 'zyx', 'mcg1049722.1']
znrf1 = dataset.volumes['znrf1']
print(znrf1.shape)
# (566, 320, 456)
```