import logging
from functools import wraps

import jsonschema

# from models.patient import Patient
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_json import as_json
from scope.schema import patient_schema
from werkzeug.local import LocalProxy


import scope.database
import scope.database.patients

patient_blueprint = Blueprint("patient_blueprint", __name__)


def validate_schema(schema_object):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(request.json, schema_object)
            except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
                # NOTE: jsonify returns a flask.Response() object with content-type header 'application/json'. Is this the best way to return the response?
                abort(
                    400,
                    jsonify(
                        message="Invalid contents.",
                        schema=error.schema,
                        error=error.message,
                    ),
                )
            return f(*args, **kwargs)

        return wrapper

    return decorator


@patient_blueprint.route("/", methods=["GET"])
@as_json
def get_patients():
    collection = scope.database.patients.PATIENTS_COLLECTION_NAME
    query = {
        "type": "patient",
    }

    return {
        "patients": scope.database.find(query, current_app.db, collection),
    }, 200


@patient_blueprint.route("/<string:patient_id>", methods=["GET"])
@as_json
def get_patient(patient_id):
    collection = scope.database.patients.PATIENTS_COLLECTION_NAME

    return scope.database.find_by_id(patient_id, current_app.db, collection), 200


@patient_blueprint.route("/", methods=["POST"])
@validate_schema(patient_schema)
@as_json
def create_patient():
    collection = scope.database.patients.PATIENTS_COLLECTION_NAME

    return {
        "inserted_id ": scope.database.insert(request.json, current_app.db, collection)
    }, 200


@patient_blueprint.route("/<string:patient_id>/", methods=["PUT"])
def update_patient(patient_id):
    pass


@patient_blueprint.route("/<string:patient_id>/", methods=["DELETE"])
def delete_patient(patient_id):
    pass
