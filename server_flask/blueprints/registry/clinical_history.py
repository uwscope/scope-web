import http
from functools import wraps

import scope.database
import scope.database.clinical_history
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import clinical_history_schema
from utils import validate_schema

registry_clinical_history_blueprint = Blueprint(
    "registry_clinical_history_blueprint", __name__, url_prefix="/patients"
)


# NOTE: Passing the patient collection name for now. Will fix this after auth workflow is finalized.
@registry_clinical_history_blueprint.route(
    "/<string:patient_collection>/clinicalhistory", methods=["GET"]
)
@as_json
def get_patient_clinical_history(patient_collection):
    context = request_context()

    result = scope.database.clinical_history.get_clinical_history(
        database=context.database, collection_name=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_clinical_history_blueprint.route(
    "/<string:patient_collection>/clinicalhistory", methods=["PUT"]
)
@validate_schema(clinical_history_schema)
@as_json
def update_patient_clinical_history(patient_collection):

    clinical_history = request.json

    if "_id" in clinical_history:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    clinical_history["_rev"] = clinical_history["_rev"] + 1

    context = request_context()

    result = scope.database.clinical_history.create_clinical_history(
        database=context.database,
        collection_name=patient_collection,
        clinical_history=clinical_history,
    )

    if result is not None:
        return str(result.inserted_id), http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
