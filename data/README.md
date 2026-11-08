# Custom Mappings

OMOP vocabulary lookup tables sourced from the [CogStack dbt_mimic_omop](https://github.com/CogStack/dbt_mimic_omop/tree/main/data/custom_mappings) repository.

Required by `step6_build_athena.py` and the dbt transformation models.

---

## Status

This directory contains all 21 CSVs required for the core MIMIC-IV pipeline.
The 2 remaining CogStack files (`gcpt_chexpert_findings.csv`, `gcpt_meas_waveforms.csv`) are intentionally excluded — they are only needed for CXR and waveform modules which are out of scope for this pipeline.
