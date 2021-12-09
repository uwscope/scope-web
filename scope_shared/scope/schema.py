import json
import pathlib

data_dir = pathlib.Path(__file__).parent / "schemas"
patient_schema = json.load(open(data_dir / "patient-schema.json"))
