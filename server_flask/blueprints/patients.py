import http
from functools import wraps

import jsonschema
import scope.database
import scope.database.patients
from flask import Blueprint, abort, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_schema

patients_blueprint = Blueprint("patients_blueprint", __name__)


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
@as_json
def create_patient():
    pass
