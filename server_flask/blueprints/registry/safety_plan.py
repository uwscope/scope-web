import http
from functools import wraps

import scope.database
import scope.database.safety_plan
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import safety_plan_schema
from utils import validate_schema

registry_safety_plan_blueprint = Blueprint(
    "registry_safety_plan_blueprint", __name__, url_prefix="/patients"
)


# NOTE: Passing the patient collection name for now. Will fix this after auth workflow is finalized.
@registry_safety_plan_blueprint.route(
    "/<string:patient_collection>/safety", methods=["GET"]
)
@as_json
def get_patient_safety_plan(patient_collection):
    context = request_context()

    result = scope.database.safety_plan.get_safety_plan(
        database=context.database, collection=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_safety_plan_blueprint.route(
    "/<string:patient_collection>/safety", methods=["PUT"]
)
@validate_schema(safety_plan_schema)
@as_json
def update_patient_safety_plan(patient_collection):

    safety_plan = request.json

    if "_id" in safety_plan:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    safety_plan["_rev"] = safety_plan["_rev"] + 1

    context = request_context()

    result = scope.database.safety_plan.create_safety_plan(
        database=context.database,
        collection=patient_collection,
        safety_plan=safety_plan,
    )

    if result is not None:
        return str(result.inserted_id), http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
