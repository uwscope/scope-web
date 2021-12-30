import http
from functools import wraps

import scope.database
import scope.database.values
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_schema
from utils import validate_schema

values_blueprint = Blueprint("values_blueprint", __name__)


# NOTE: Passing the patient collection name for now. Will fix this after auth workflow is finalized.
# Other option could be the patient identity id because the collection name is `patient_{identity_id}`.
@values_blueprint.route("/<string:patient_collection>", methods=["GET"])
@as_json
def get_patient_values(patient_collection):
    context = request_context()

    result = scope.database.values.get_values(
        database=context.database, collection=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@values_blueprint.route("/<string:patient_collection>", methods=["PUT"])
@as_json
def update_patient_values(patient_collection):

    values_inventory = request.json

    context = request_context()

    result = scope.database.values.create_values(
        database=context.database,
        collection=patient_collection,
        values_inventory=values_inventory,
    )

    if result is not None:
        return values_inventory, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)
