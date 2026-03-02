# Supported Metadata Fields

## `species`

Category of biological classification comprising related organisms or populations potentially capable of interbreeding, and being designated by a binomial that consists of the name of a genus followed by a Latin or latinized uncapitalized noun or adjective.

openMINDS type: [https://openminds.om-i.org/types/Species](https://openminds.om-i.org/types/Species)

**Valid values (26):** Berghia stephanieae, Bos taurus, Caenorhabditis elegans, Callithrix jacchus, Cervus elaphus, Chlorocebus aethiops sabaeus, Chlorocebus pygerythrus, Cricetulus griseus, Danio rerio, Drosophila melanogaster, Felis catus, Homo sapiens, Macaca fascicularis, Macaca fuscata, Macaca mulatta, Macaca nemestrina, Meriones unguiculatus, Monodelphis domestica, Mus musculus, Mustela putorius, Mustela putorius furo, Ovis aries, Quiscalus mexicanus, Rattus norvegicus, Sus scrofa domesticus, Trachemys scripta elegans

---

## `coordinate_space`

The BrainGlobe atlas coordinate space the volume is registered to. Stored as `{name, version}`.

openMINDS type: [https://openminds.om-i.org/types/CommonCoordinateSpace](https://openminds.om-i.org/types/CommonCoordinateSpace)

**Valid values:** Must match a BrainGlobe atlas coordinate space name and version (e.g. `{"name": "allen-adult-mouse-ccf-space", "version": "2015"}`).

---


## `technique`

Method of accomplishing a desired aim.

openMINDS type: [https://openminds.om-i.org/types/Technique](https://openminds.om-i.org/types/Technique)

<details>
<summary><strong>Valid values (194)</strong></summary>

3D computer graphic modeling, 3D polarized light imaging, 3D scanning, CLARITY/TDE, DAB staining, DAPi staining, DNA methylation analysis, DNA sequencing, Golgi staining, H&E staining, HPC simulation, Hoechst staining, Nissl staining, RNA sequencing, Raman spectroscopy, SDS-digested freeze-fracture replica labeling, SWITCH immunohistochemistry, TDE clearing, Timm's staining, activity modulation technique, anaesthesia administration, anaesthesia monitoring, anaesthesia technique, angiography, anterograde tracing, autoradiography, avidin-biotin complex staining, beta-galactosidase staining, biocytin staining, blood sampling, brightfield microscopy, calcium imaging, callosotomy, cell attached patch clamp, coherent Stokes Raman spectroscopy, coherent anti-Stokes Raman spectroscopy, computer tomography, confocal microscopy, contrast agent administration, contrast enhancement, cortico-cortical evoked potential mapping, craniotomy, cryosectioning, current clamp, darkfield microscopy, differential interference contrast microscopy, diffusion fixation technique, diffusion spectrum magnetic resonance imaging, diffusion tensor imaging, diffusion-weighted imaging, dual-view inverted selective plane illumination microscopy, electrocardiography, electrocorticography, electroencephalography, electromyography, electron microscopy, electron tomography, electrooculography, electroporation, enzyme-linked immunosorbent assay, epidermal electrophysiology technique, epidural electrocorticography, epifluorescent microscopy, extracellular electrophysiology, eye movement tracking, fixation technique, fluorescence microscopy, focused ion beam scanning electron microscopy, functional magnetic resonance imaging, gene expression measurement, gene knockin, gene knockout, genome-wide association study, heavy metal negative staining, high-density electroencephalography, high-field functional magnetic resonance imaging, high-field magnetic resonance imaging, high-field structural magnetic resonance imaging, high-resolution scanning, high-speed video recording, high-throughput scanning, histochemistry, immunohistochemistry, immunoprecipitation, implant surgery, in situ hybridisation, infrared differential interference contrast video microscopy, injection, intracellular electrophysiology, intracellular injection, intracranial electroencephalography, intraperitoneal injection, intravenous injection, iontophoresis, iontophoretic microinjection, light microscopy, light sheet fluorescence microscopy, magnetic resonance imaging, magnetic resonance spectroscopy, magnetization transfer imaging, magnetoencephalography, mass spectrometry, micro computed tomography, microtome sectioning, motion capture, multi photon fluorescence microscopy, multi-compartment modeling, multi-electrode extracellular electrophysiology, multiple whole cell patch clamp, myelin staining, myelin water imaging, near infrared spectroscopy, neuromorphic simulation, nonlinear optical microscopy, nucleic acid extraction, optical coherence tomography, optical coherence tomography angiography, optogenetic inhibition, oral administration, organ extraction, patch clamp, perfusion fixation technique, perfusion technique, perturbational complexity index measurement, phase contrast microscopy, phase-contrast x-ray imaging, phase‐contrast x‐ray computed tomography, photoactivation, photoinactivation, photoplethysmography, polarized light microscopy, population receptive field mapping, positron emission tomography, pressure injection, primary antibody staining, pseudo-continuous arterial spin labeling, psychological testing, pupillometry, quantification, quantitative magnetic resonance imaging, quantitative susceptibility mapping, receptive field mapping, reporter gene based expression measurement, reporter protein based expression measurement, retinotopic mapping, retrograde tracing, rule-based modeling, scanning electron microscopy, scattered light imaging, secondary antibody staining, serial block face scanning electron microscopy, serial section transmission electron microscopy, sharp electrode intracellular electrophysiology, silver staining, simulation, single cell RNA sequencing, single electrode extracellular electrophysiology, single electrode juxtacellular electrophysiology, single gene analysis, single nucleotide polymorphism detection, sodium MRI, sonography, standardization, stereoelectroencephalography, stereology, stereotactic surgery, structural magnetic resonance imaging, structural neuroimaging, subcutaneous injection, subdural electrocorticography, super resolution microscopy, susceptibility weighted imaging, tetrode extracellular electrophysiology, time-of-flight magnetic resonance angiography, tissue clearing, tract tracing, transcardial perfusion fixation technique, transcardial perfusion technique, transmission electron microscopy, two-photon fluorescence microscopy, ultra high-field functional magnetic resonance imaging, ultra high-field magnetic resonance imaging, ultra high-field magnetic resonance spectroscopy, ultra high-field structural magnetic resonance imaging, vibratome sectioning, video tracking, video-oculography, virus-mediated transfection, voltage clamp, voltage sensitive dye imaging, weighted correlation network analysis, whole cell patch clamp, whole genome sequencing, widefield fluorescence microscopy

</details>

---

## `injection_target`

Specific brain regions which were injection targets. Nested with the annotation set that defines the region acronyms.

openMINDS type: [https://openminds.om-i.org/props/anatomicalLocation](https://openminds.om-i.org/props/anatomicalLocation)

**Structure:**
```json
{
  "regions": ["MOp"],
  "annotation_set": {
    "name": "allen-adult-mouse-annotation",
    "version": "2017"
  }
}
```

**Valid values for `regions`:** Constrained to terminology acronyms defined by the specified `annotation_set` (e.g. "MOp", "VISp", "AMY" for `allen-adult-mouse-annotation`).

---

## `injection_coordinate`

Specific coordinate in CCF coordinates in the related coordinate space


---

## `developmental_stage`

Distinct life cycle class that is defined by a similar age or age range (developmental stage) within a group of individual beings.

openMINDS type: [https://openminds.om-i.org/types/AgeCategory](https://openminds.om-i.org/types/AgeCategory)

**Valid values (10):** adolescent, adult, embryo, infant, juvenile, late adult, neonate, perinatal, prime adult, young adult

---

## `biological_sex`

Differentiation of individuals of most species (animals and plants) based on the type of gametes they produce.

openMINDS type: [https://openminds.om-i.org/types/BiologicalSex](https://openminds.om-i.org/types/BiologicalSex)

**Valid values (4):** female, hermaphrodite, male, not detectable

---

## `measured_quantity`

What the voxel values in a 3D volume actually represent.

Inspired by openMINDS [MeasuredQuantity](https://openminds.om-i.org/types/MeasuredQuantity), but using a custom controlled vocabulary relevant to volumetric imaging data.

**Valid values:** fluorescence intensity, cell density, gene expression level, optical density, T1 relaxation time, T2 relaxation time, fractional anisotropy, mean diffusivity, cerebral blood flow, probability map, binary mask
