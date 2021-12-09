from functools import wraps

import jsonschema
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
from models.patient import Patient
from scope.schema import patient_schema

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


# NOTE: "collection_name=<>" can be hard coded in the model file. Keeping it here for now.
patient = Patient(collection_name="patient_collection")


@patient_blueprint.route("/", methods=["GET"])
@as_json
def get_patients():
    response = patient.find({})
    return response, 200


@patient_blueprint.route("/<string:patient_id>", methods=["GET"])
@as_json
def get_patient(patient_id):
    response = patient.find_by_id(patient_id)
    return response, 200


@patient_blueprint.route("/", methods=["POST"])
@validate_schema(patient_schema)
@as_json
def create_patient():
    response = patient.create(request.json)
    return response, 200


@patient_blueprint.route("/<string:patient_id>/", methods=["PUT"])
def update_patient(patient_id):
    pass


@patient_blueprint.route("/<string:patient_id>/", methods=["DELETE"])
def delete_patient(patient_id):
    pass
