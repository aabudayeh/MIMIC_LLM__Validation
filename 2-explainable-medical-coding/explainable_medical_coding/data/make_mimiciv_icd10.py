"""
Script to create the mimiciv_icd10cm dataset from the mimiciv dataset.
"""

from pathlib import Path

import polars as pl
import json
import pandas as pd
from explainable_medical_coding.utils.data_helper_functions import remove_rare_codes, load_filtered_mimiciv



new_folder_path = Path("data/processed/mimiciv_icd10")
# create folder
new_folder_path.mkdir(parents=True, exist_ok=True)

# ========== Changed Code ==========
filtered_path = "data/processed/mimiciv_filtered.parquet"
data = load_filtered_mimiciv("data/processed/mimiciv.parquet", "../1-llm_label_refinement/data/processed_data/combined.json", filtered_path)
# ========== Changed Code ==========

splits = pl.read_ipc("data/splits/mimiciv_icd10_split.feather")
data = data.join(splits, on="_id")

# remove not used columns
data = data.drop(["note_seq", "charttime", "storetime"])

# only keep ICD-10 codes
data = data.filter(
    (pl.col("diagnosis_code_type") == "icd10cm")
    | (pl.col("procedure_code_type") == "icd10pcs")
)

# remove rare codes
data = remove_rare_codes(data, ["diagnosis_codes", "procedure_codes"], 10)

# drop duplicates
data = data.unique(subset=["_id"])

# filter out rows with no codes
data = data.filter(
    pl.col("diagnosis_codes").is_not_null() | pl.col("procedure_codes").is_not_null()
)

train = data.filter(pl.col("split") == "train")
val = data.filter(pl.col("split") == "val")
test = data.filter(pl.col("split") == "test")

# remove split column
train = train.drop("split")
val = val.drop("split")
test = test.drop("split")

# save files as parquet
train.write_parquet(new_folder_path / "train.parquet")
val.write_parquet(new_folder_path / "val.parquet")
test.write_parquet(new_folder_path / "test.parquet")
