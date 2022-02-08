import flask
import flask_json
import pymongo.errors

import scope.database
import scope.database.patient.safety_plan
from request_context import request_context
from scope.schema import safety_plan_schema
from utils import validate_schema

safety_plan_blueprint = flask.Blueprint(
    "safety_plan_blueprint",
    __name__,
)


@safety_plan_blueprint.route(
    "/<string:patient_id>/safetyplan",
    methods=["GET"],
)
@flask_json.as_json
def get_safety_plan(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    document_retrieved = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection,
    )
    if document_retrieved is None:
        context.abort_document_not_found()

    return {
        "safetyplan": document_retrieved
    }


@safety_plan_blueprint.route(
    "/<string:patient_id>/safetyplan",
    methods=["PUT"],
)
@validate_schema(safety_plan_schema)
@flask_json.as_json
def put_safety_plan(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json

    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        context.abort_put_with_id()

    # Store the document
    try:
        result = scope.database.patient.safety_plan.put_safety_plan(
            collection=patient_collection,
            safety_plan=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.safety_plan.get_safety_plan(
            collection=patient_collection
        )
        context.abort_revision_conflict(
            document={
                "safetyplan": document_conflict,
            }
        )
    else:
        return {
            "safetyplan": result.document,
        }
