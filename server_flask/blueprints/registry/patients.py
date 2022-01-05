import http
from functools import wraps

import scope.database
import scope.database.patients
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_schema
from utils import validate_schema

registry_patients_blueprint = Blueprint(
    "registry_patients_blueprint", __name__, url_prefix="/patients"
)


@registry_patients_blueprint.route("/", methods=["GET"])
@as_json
def get_patients():
    context = request_context()

    patients = scope.database.patients.get_patients(database=context.database)
    return {"patients": patients}, http.HTTPStatus.OK


@registry_patients_blueprint.route("/<string:patient_collection>", methods=["GET"])
@as_json
def get_patient(patient_collection):
    context = request_context()

    result = scope.database.patients.get_patient(
        database=context.database, collection=patient_collection
    )

    if result is not None:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_patients_blueprint.route("/", methods=["POST"])
@validate_schema(patient_schema)
@as_json
def create_patient():

    patient = request.json

    context = request_context()

    # Creates a patient collection of name `patient_{identity["_id"]` and inserts all the subschema documents.
    created_patient = scope.database.patients.create_patient(
        database=context.database, patient=patient
    )

    return created_patient, http.HTTPStatus.OK
