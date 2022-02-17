import http
from functools import wraps

import scope.database
import scope.database.patient.assessment_logs
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import assessment_log_schema
from utils import validate_schema

registry_assessment_logs_blueprint = Blueprint(
    "registry_assessment_logs_blueprint", __name__, url_prefix="/patients"
)


@registry_assessment_logs_blueprint.route(
    "/<string:patient_collection>/assessmentlogs", methods=["GET"]
)
@as_json
def get_assessment_logs(patient_collection):
    context = request_context()

    result = scope.database.patient.assessment_logs.get_assessment_logs(
        database=context.database, collection_name=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_assessment_logs_blueprint.route(
    "/<string:patient_collection>/assessmentlogs", methods=["POST"]
)
@validate_schema(
    schema=assessment_log_schema,
)
@as_json
def create_assessment_log(patient_collection):
    """
    Adds a new assessment log in the patient record and returns the assessment log.
    """

    assessment_log = request.json

    if "_id" in assessment_log:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    context = request_context()

    result = scope.database.patient.assessment_logs.create_assessment_log(
        database=context.database,
        collection_name=patient_collection,
        assessment_log=assessment_log,
    )

    if result is not None:
        assessment_log.update({"_id": str(result.inserted_id)})
        return assessment_log, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422


@registry_assessment_logs_blueprint.route(
    "/<string:patient_collection>/assessmentlogs/<string:log_id>", methods=["GET"]
)
@as_json
def get_assessment_log(patient_collection, log_id):
    context = request_context()

    result = scope.database.patient.assessment_logs.get_assessment_log(
        database=context.database,
        collection_name=patient_collection,
        log_id=log_id,
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_assessment_logs_blueprint.route(
    "/<string:patient_collection>/assessmentlogs/<string:log_id>", methods=["PUT"]
)
@validate_schema(
    schema=assessment_log_schema,
)
@as_json
def update_assessment_log(patient_collection, log_id):

    assessment_log = request.json

    if "_id" in assessment_log:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    assessment_log["_rev"] += 1

    # NOTE: Assume client is not sending log_id as part of json.
    assessment_log.update({"_log_id": log_id})

    context = request_context()

    result = scope.database.patient.assessment_logs.update_assessment_log(
        database=context.database,
        collection_name=patient_collection,
        assessment_log=assessment_log,
    )

    if result is not None:
        assessment_log.update({"_id": str(result.inserted_id)})
        return assessment_log, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
