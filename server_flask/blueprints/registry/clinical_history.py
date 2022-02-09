import flask
import flask_json
import pymongo.errors
import scope.database
import scope.database.patient.clinical_history
from request_context import request_context
from scope.schema import clinical_history_schema
from utils import validate_schema

clinical_history_blueprint = flask.Blueprint("clinical_history_blueprint", __name__)


@clinical_history_blueprint.route(
    "/<string:patient_id>/clinicalhistory", methods=["GET"]
)
@flask_json.as_json
def get_clinical_history(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.clinical_history.get_clinical_history(
        collection=patient_collection,
    )
    if document is None:
        context.abort_document_not_found()

    return {
        "clinicalhistory": document,
    }


@clinical_history_blueprint.route(
    "/<string:patient_id>/clinicalhistory", methods=["PUT"]
)
@validate_schema(clinical_history_schema)
@flask_json.as_json
def put_clinical_history(patient_id):

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
        result = scope.database.patient.clinical_history.put_clinical_history(
            collection=patient_collection,
            clinical_history=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.clinical_history.get_clinical_history(
                collection=patient_collection
            )
        )
        context.abort_revision_conflict(
            document={
                "clinicalhistory": document_conflict,
            }
        )
    else:
        return {
            "clinicalhistory": result.document,
        }
