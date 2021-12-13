from functools import wraps

import jsonschema

# from models.patient import Patient
from database import find, find_by_id, get_db, insert
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

db = LocalProxy(get_db)

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
    query = {}
    collection = "patient_collection"
    return {"patients": find(query, db, collection)}, 200


@patient_blueprint.route("/<string:patient_id>", methods=["GET"])
@as_json
def get_patient(patient_id):
    collection = "patient_collection"
    return find_by_id(patient_id, db, collection), 200


@patient_blueprint.route("/", methods=["POST"])
@validate_schema(patient_schema)
@as_json
def create_patient():
    collection = "patient_collection"
    return {"inserted_id ": insert(request.json, db, collection)}, 200


@patient_blueprint.route("/<string:patient_id>/", methods=["PUT"])
def update_patient(patient_id):
    pass


@patient_blueprint.route("/<string:patient_id>/", methods=["DELETE"])
def delete_patient(patient_id):
    pass
