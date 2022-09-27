# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# Extract the `archive_{}_{release}_{date}.zip` folder in data folder.

import pandas as pd
import pathlib

paths = pathlib.Path("./data/patients").glob("*.json")
patients_df = pd.DataFrame([pd.read_json(p, typ="series") for p in paths])

patients_df.head()

# Number of patients
patients_df["patientId"].nunique()


