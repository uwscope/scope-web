import flask
import flask_json
import pymongo.errors

from request_context import request_context
import request_utils
import scope.database
import scope.database.patient.patient_profile
import scope.database.patients
from scope.schema import patient_profile_schema

patient_profile_blueprint = flask.Blueprint(
    "patient_profile_blueprint",
    __name__,
)


@patient_profile_blueprint.route(
    "/<string:patient_id>/profile",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_profile(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Retrieve the current patient profile
    document = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection,
    )
    if document is None:
        context.abort_document_not_found()

    return {
        "profile": document,
    }


@patient_profile_blueprint.route(
    "/<string:patient_id>/profile",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=patient_profile_schema,
    key="profile",
)
@flask_json.as_json
def put_patient_profile(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["profile"]

    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        context.abort_put_with_id()

    # Store the document
    try:
        result = scope.database.patient.patient_profile.put_patient_profile(
            collection=patient_collection,
            patient_profile=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.patient_profile.get_patient_profile(
            collection=patient_collection
        )
        context.abort_revision_conflict(
            document={
                "profile": document_conflict,
            }
        )
    else:
        return {
            "profile": result.document,
        }
