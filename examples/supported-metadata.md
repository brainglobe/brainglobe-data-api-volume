| Python `kwarg` | openMINDS Origin | Description & Examples |
| :--- | :--- | :--- |
| `species` | `subjectSpecimen.species` | The organism studied. <br>*Examples: "Mus musculus", "Danio rerio", "Homo sapiens"* |
| `atlas_space` | `coordinateSpace` (SANDS) | The BrainGlobe reference space the volume is registered to.<br>*Examples: "allen_mouse_25um", "mpin_zfish_1um"* |
| `technique` | `technique` | The method used to acquire or process the data. <br>*Examples: "viral tracing", "in situ hybridization", "fMRI", "two-photon fluorescence microscopy"* |
| `experimental_approach` | `experimentalApproach` | The overarching scientific domain of the dataset. <br>*Examples: "neuroanatomy", "transcriptomics", "neuroimaging"* |
| `anatomical_target` | `anatomicalLocation` (SANDS) | Specific brain regions tied to the experiment (e.g., a viral injection site, a tumor location, or an ROI). Uses atlas acronyms. <br>*Examples: "MOp", "VISp", "amygdala"* |
| `developmental_stage` | `subjectSpecimen.developmentalStage` | The age or life stage of the subjects. <br>*Examples: "P56", "adult", "embryo", "E15.5"* |
| `biological_sex` | `subjectSpecimen.biologicalSex` | The sex of the subjects in the dataset. <br>*Examples: "male", "female", "pooled"* |
| `measured_quantity` | `measuredQuantity` | What the voxel values in the 3D heatmap actually represent. <br>*Examples: "projection density", "gene expression level", "cell density", "BOLD signal"* |
