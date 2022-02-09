import flask
import flask_json
import pymongo.errors
import scope.database
import scope.database.patient.values_inventory
from request_context import request_context
from scope.schema import values_inventory_schema
from utils import validate_schema

values_inventory_blueprint = flask.Blueprint("values_inventory_blueprint", __name__)


@values_inventory_blueprint.route("/<string:patient_id>/values", methods=["GET"])
@flask_json.as_json
def get_values_inventory(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.values_inventory.get_values_inventory(
        collection=patient_collection,
    )
    if document is None:
        context.abort_document_not_found()

    return {
        "valuesinventory": document,
    }


@values_inventory_blueprint.route("/<string:patient_id>/values", methods=["PUT"])
@validate_schema(values_inventory_schema)
@flask_json.as_json
def put_patient_values(patient_id):

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
        result = scope.database.patient.values_inventory.put_values_inventory(
            collection=patient_collection,
            values_inventory=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.values_inventory.get_values_inventory(
                collection=patient_collection
            )
        )
        context.abort_revision_conflict(
            document={
                "valuesinventory": document_conflict,
            }
        )
    else:
        return {
            "valuesinventory": result.document,
        }
