import json

from flask import Flask, request
from flask_cors import CORS
from flask_json import FlaskJSON, as_json
from markupsafe import escape

from assessments import get_supported_assessments
from fake import getFakePatient, getRandomFakePatients
from utils import parseInt

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
## - differentiate development versus production execution
##   (e.g., should not have debugger running in production, for security reasons)

@app.route("/auth")
@as_json
def auth():
    return {"name": "Luke Skywalker", "authToken": "my token"}


@app.route("/patients")
@as_json
def get_patients():
    return {"patients": patients}


@app.route("/patient/<mrn>", methods=["GET"])
@as_json
def get_patient_data(mrn):
    if request.method == "GET":
        if mrn == None or patient_map.get(mrn, None) == None:
            return "Patient not found", 404

        return patient_map[mrn]

    else:
        return "Method not allowed", 405


@app.route("/app/config", methods=["GET"])
@as_json
def get_assessments():
    if request.method == "GET":
        return {"assessments": get_supported_assessments()}

    else:
        return "Method not allowed", 405
