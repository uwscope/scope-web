import json

from flask import Flask, request
from flask_cors import CORS
from markupsafe import escape

from fake import getFakePatient, getRandomFakePatients
from utils import parseInt

from flask_json import as_json, FlaskJSON

app = Flask(__name__)
CORS(app)
FlaskJSON(app)


## Temporary store for patients
patients = getRandomFakePatients()
patient_map = {p["MRN"]: p for p in patients}

## API TODOs:
## - check method
## - check parameters
## - return appropriate error message and code

@app.route("/auth")
@as_json
def auth():
    return {
        "name": "Luke Skywalker",
        "authToken": "my token"
    }

@app.route("/patients")
@as_json
def get_patients():
    return {"patients": patients}


@app.route("/patient/<mrn>", methods=["GET"])
@as_json
def get_patient_data(mrn):
    if request.method == "GET":
        patient_mrn = parseInt(escape(mrn))

        if patient_mrn == None or patient_map.get(patient_mrn, None) == None:
            return "Patient not found", 404

        return patient_map[patient_mrn]

    else:
        return "Method not allowed", 405
