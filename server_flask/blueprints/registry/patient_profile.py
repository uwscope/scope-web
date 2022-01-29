import http
from functools import wraps

import scope.database
import scope.database.patient.patient_profile
import scope.database.patients
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json

from request_context import request_context
from scope.schema import patient_profile_schema
from utils import validate_schema

patient_profile_blueprint = Blueprint(
    "registry_patient_profile_blueprint",
    __name__,
)


@patient_profile_blueprint.route(
    "/<string:patient_id>/patient_profile", methods=["GET"],
)
@as_json
def get_patient_profile(patient_id):
    # TODO: Require authentication

    context = request_context()

    # Use patient ID to confirm validity and obtain collection
    # TODO: As part of authentication, determine if we can cache this.
    #       Otherwise, maybe an annotation or enhance context to reduce code repetition.
    patient_document = scope.database.patients.get_patient(
        database=context.database,
        patient_id=patient_id,
    )
    if patient_document is None:
        abort(http.HTTPStatus.NOT_FOUND)

    # Obtain patient collection
    patient_collection = context.database.get_collection(
        patient_document["collection"]
    )

    # Retrieve the current patient profile
    result = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection
    )
    if patient_document is None:
        # TODO: This is the correct semantics, evaluate impact on client.
        abort(http.HTTPStatus.NOT_FOUND)

    return result

#
#
# @registry_patient_profile_blueprint.route(
#     "/<string:patient_collection>/profile", methods=["PUT"]
# )
# @validate_schema(patient_profile_schema)
# @as_json
# def update_patient_values(patient_collection):
#
#     patient_profile = request.json
#
#     if "_id" in patient_profile:
#         abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
#
#     # Update _rev
#     patient_profile["_rev"] += 1
#
#     context = request_context()
#
#     result = scope.database.patient.patient_profile.create_patient_profile(
#         database=context.database,
#         collection_name=patient_collection,
#         patient_profile=patient_profile,
#     )
#
#     if result is not None:
#         return str(result.inserted_id), http.HTTPStatus.OK
#     else:
#         # NOTE: Send back the latest version of the document. Hold off on that.
#         abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
