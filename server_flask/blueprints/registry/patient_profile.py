import http
from functools import wraps

import scope.database
import scope.database.patient.patient_profile
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import patient_profile_schema
from utils import validate_schema

registry_patient_profile_blueprint = Blueprint(
    "registry_patient_profile_blueprint", __name__, url_prefix="/patients"
)


# NOTE: Passing the patient collection name for now. Will fix this after auth workflow is finalized.
@registry_patient_profile_blueprint.route(
    "/<string:patient_collection>/profile", methods=["GET"]
)
@as_json
def get_patient_values(patient_collection):
    context = request_context()

    result = scope.database.patient.patient_profile.get_patient_profile(
        database=context.database, collection_name=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_patient_profile_blueprint.route(
    "/<string:patient_collection>/profile", methods=["PUT"]
)
@validate_schema(patient_profile_schema)
@as_json
def update_patient_values(patient_collection):

    patient_profile = request.json

    if "_id" in patient_profile:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    patient_profile["_rev"] += 1

    context = request_context()

    result = scope.database.patient.patient_profile.create_patient_profile(
        database=context.database,
        collection_name=patient_collection,
        patient_profile=patient_profile,
    )

    if result is not None:
        return str(result.inserted_id), http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
