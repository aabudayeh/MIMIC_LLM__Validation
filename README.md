# Evidence-Grounded LLM Validation of MIMIC-IV ICD Labels
_Reproducible code and data preparation for label refinement and model replication._

> Folder layout (run each subrepo from its own CWD)
>
> .
> ├─ 1-llm_label_refinement/               # LLM workflow → produces processed_data/combined.json  
> ├─ 2-explainable-medical-coding/         # PLM-ICD (multi-GPU) training/testing  
> └─ 3-medical-coding-reproducibility/     # LAAT, CAML, MultiResCNN, Bi-GRU, CNN  
>
> Paths between folders are relative (e.g., ../1-llm_label_refinement/processed_data/combined.json)

## Summary
- Reproduce [Edin et al. (2023) – Automated Medical Coding on MIMIC-III and MIMIC-IV](https://arxiv.org/abs/2304.10909) preprocessing and validate ICD-10 labels using an LLM.  
- Generate refined label sets: **EV (Evidence-Verified)** and **ER (Evidence-Replaced)**.  
- Filter full dataset to LLM-processed note_ids and replicate training and testing of six models (PLM-ICD, LAAT, CAML, MultiResCNN, Bi-GRU, CNN) on original and refined label sets.
- Figure results are in 3-medical-coding-reproducibility/files/figures

## 0) Requirements
- Python ≥ 3.10, CUDA recommended (for GPU acceleration)  
- Access to MIMIC-IV v2.2 (PhysioNet credential required)  
- Recommended: use a virtual environment and install dependencies per subrepo requirements.

---

## 1) LLM Label Refinement (folder: 1-llm_label_refinement)
Notebooks (run sequentially):

1. **1-processing.ipynb** – Downloads and preprocesses raw MIMIC-IV data, replicating Edin et al.’s steps, and produces mimiciv_icd10 files and dictionaries.  
2. **2-create_benchmark.ipynb** – Builds processed inputs JSON for LLM inference. Resumable via checkpoints (useful for large batches).  
3. **3-validate.ipynb** – Merges LLM outputs with note IDs to produce processed_data/combined.json (used downstream).  
4. **4-manual_review.ipynb** – Optional manual correction or review of LLM outputs.

**Main output:**  
1-llm_label_refinement/processed_data/combined.json

---

## 2) PLM-ICD (folder: 2-explainable-medical-coding)
Scope: Train and test PLM-ICD on filtered note_ids from the LLM workflow. Code edits are marked with "# Changed Code".

Switch target label sets by editing:  
explainable_medical_coding/config/data/mimiciv_icd10.yaml  
Set target_column_name to one of:
- mimic_codes_y  → Original MIMIC (OM)  
- llm_validated_y  → Evidence-Verified (EV)  
- llm_accurate_y  → Evidence-Replaced (ER)

Notes:  
- Paths assume combined.json is available at ../1-llm_label_refinement/processed_data/combined.json  
- Multi-GPU utilization added to train_plm.py

---

## 3) Baselines (folder: 3-medical-coding-reproducibility)
Used for LAAT, CAML, MultiResCNN, Bi-GRU, and CNN. (PLM-ICD is trained in the previous repo.)

Workflow:
1. Prepare the full processed dataset:  
   python prepare_data/prepare_mimiciv.py  
   → Generates files/data/mimiciv_icd10/mimiciv_icd10.feather (full, proccessed, unfiltered)

2. Generate filtered targets for each label set (OM, EV, ER) by running:  
   files/data/mimiciv_icd10/generate_targets.ipynb
   → Uses: filtered parquet file generated from explainable-medical-coding repo.
   → Produces:  
     files/data/mimiciv_icd10/filtered_targets/mimic_codes_y/mimiciv_icd10.feather  
     files/data/mimiciv_icd10/filtered_targets/llm_validated_y/mimiciv_icd10.feather  
     files/data/mimiciv_icd10/filtered_targets/llm_accurate_y/mimiciv_icd10.feather  

4. Select which label set to train on:  
   Copy the desired mimiciv_icd10.feather from its subfolder into:  
   files/data/mimiciv_icd10/mimiciv_icd10.feather  
   (Swap the file to change target label sets.)

---

## Reproduce the Full Pipeline
1) LLM Label Refinement  
   cd 1-llm_label_refinement  
   run notebooks 1 to 3

2) PLM-ICD  
   cd ../2-explainable-medical-coding
   prep per original repo instructions
   set target_column_name in config and train model

4) Baselines  
   cd ../3-medical-coding-reproducibility  
   python prepare_data/prepare_mimiciv.py  
   run generate_targets.ipynb  
   copy filtered mimiciv_icd10.feather  
   run model training (main.py)

---

## Citation
If you use this code or refined labels, please cite:
- MIMIC-IV: Johnson AEW et al., *Scientific Data*, 2023;10(1). doi:10.1038/s41597-022-01899-x
- Edin J et al., *SIGIR 2023* (arXiv:2304.10909)  
- This project

---

## License
Upstream repositories retain their original licenses. 
