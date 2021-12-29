import http
from functools import wraps

import scope.database
import scope.database.patients
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_schema
from utils import validate_schema

patients_blueprint = Blueprint("patients_blueprint", __name__)


@patients_blueprint.route("/", methods=["GET"])
@as_json
def get_patients():
    context = request_context()

    patients = scope.database.patients.get_patients(database=context.database)

    return {"patients": patients}, http.HTTPStatus.OK


@patients_blueprint.route("/<string:patient_id>", methods=["GET"])
@as_json
def get_patient(patient_id):
    context = request_context()

    result = scope.database.patients.get_patient(
        database=context.database, id=patient_id
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@patients_blueprint.route("/", methods=["POST"])
@validate_schema(patient_schema)
@as_json
def create_patient():
    current_app.logger.info(request.json)

    patient = request.json

    context = request_context()

    # Creates a patient collection of name `patient_{identity["_id"]` and inserts all the subschema documents.
    patient_collection_name = scope.database.patients.create_patient_collection(
        database=context.database, patient=patient
    )

    current_app.logger.info(patient_collection_name)

    return patient_collection_name, http.HTTPStatus.OK
