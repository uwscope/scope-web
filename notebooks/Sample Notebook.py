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

# Provide full path to encrypted archive
archive_path = input()

# Provide password to encrypted archive
password = input()

# +
import pandas as pd
import pathlib

from scope.populate.data.archive import Archive
# -

archive = Archive.read_archive(archive_path=pathlib.Path(archive_path), password=password)

all_documents_df = pd.DataFrame.from_dict(archive.entries, orient="index")

patients_df = all_documents_df[all_documents_df["_type"] == "patientIdentity"]

patients_df.head()

# Number of patients
patients_df["patientId"].nunique()
