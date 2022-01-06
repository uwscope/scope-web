import http
from functools import wraps

import scope.database
import scope.database.values_inventory
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import values_inventory_schema
from utils import validate_schema

registry_values_inventory_blueprint = Blueprint(
    "registry_values_inventory_blueprint", __name__, url_prefix="/patients"
)


# NOTE: Passing the patient collection name for now. Will fix this after auth workflow is finalized.
@registry_values_inventory_blueprint.route(
    "/<string:patient_collection>/values", methods=["GET"]
)
@as_json
def get_patient_values(patient_collection):
    context = request_context()

    result = scope.database.values_inventory.get_values_inventory(
        database=context.database, collection=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_values_inventory_blueprint.route(
    "/<string:patient_collection>/values", methods=["PUT"]
)
@validate_schema(values_inventory_schema)
@as_json
def update_patient_values(patient_collection):

    values_inventory = request.json

    if "_id" in values_inventory:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    values_inventory["_rev"] = values_inventory["_rev"] + 1

    context = request_context()

    result = scope.database.values_inventory.create_values_inventory(
        database=context.database,
        collection=patient_collection,
        values_inventory=values_inventory,
    )

    if result is not None:
        return str(result.inserted_id), http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
