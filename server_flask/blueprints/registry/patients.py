import http
from functools import wraps

from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_schema
from utils import validate_schema


import fake
import scope.database.patients

# @app.route("/patients")
# @as_json
# def get_patients():
#     return {"patients": patients}
#
#
# @app.route("/patient/<recordId>", methods=["GET"])
# @as_json
# def get_patient_data(recordId):
#     if request.method == "GET":
#         if recordId == None or patient_map.get(recordId, None) == None:
#             return "Patient not found", 404
#
#         return patient_map[recordId]
#
#     else:
#         return "Method not allowed", 405


# Temporary store for patients
# fake_patients = fake.getRandomFakePatients()
# fake_patient_map = {p["identity"]["identityId"]: p for p in fake_patients}

FAKE_PATIENT_MAP = {}


patients_blueprint = Blueprint(
    "patients_blueprint", __name__,
)


@patients_blueprint.route("/patients", methods=["GET"])
@as_json
def get_patients():
    context = request_context()

    patients = scope.database.patients.get_patients(
        database=context.database,
    )

    # TODO: Remove fake data generation
    # Ensure fake data exists for each patient
    for patient_current in patients:
        patient_id = patient_current["_set_id"]
        if patient_id not in FAKE_PATIENT_MAP:
            FAKE_PATIENT_MAP[patient_id] = fake.getFakePatient()
            FAKE_PATIENT_MAP[patient_id]["identity"]["identityId"] = patient_id



    return {
        "patients": list(FAKE_PATIENT_MAP.values())
    }

    # patients = scope.database.patient.patients.get_patients(database=context.database)
    # return {"patients": patients}, http.HTTPStatus.OK


# @registry_patients_blueprint.route("/<string:patient_collection>", methods=["GET"])
# @as_json
# def get_patient(patient_collection):
#     context = request_context()
#
#     result = scope.database.patient.patients.get_patient(
#         database=context.database, collection_name=patient_collection
#     )
#
#     if result is not None:
#         return result, http.HTTPStatus.OK
#     else:
#         abort(http.HTTPStatus.NOT_FOUND)
#
#
# @registry_patients_blueprint.route("/", methods=["POST"])
# @validate_schema(patient_schema)
# @as_json
# def create_patient():
#
#     patient = request.json
#
#     context = request_context()
#
#     created_patient = scope.database.patient.patients.create_patient(
#         database=context.database, patient=patient
#     )
#     if created_patient is not None:
#         return created_patient, http.HTTPStatus.OK
#     else:
#         abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
