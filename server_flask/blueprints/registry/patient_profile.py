import flask
import flask_json
import http
import pymongo.errors

from request_context import request_context
import scope.database
import scope.database.patient.patient_profile
import scope.database.patients
from scope.schema import patient_profile_schema
from utils import validate_schema

patient_profile_blueprint = flask.Blueprint(
    "patient_profile_blueprint",
    __name__,
)


@patient_profile_blueprint.route(
    "/<string:patient_id>/patient_profile",
    methods=["GET"],
)
@flask_json.as_json
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
        flask.abort(http.HTTPStatus.NOT_FOUND)

    # Obtain patient collection
    patient_collection = context.database.get_collection(patient_document["collection"])

    # Retrieve the current patient profile
    document_retrieved = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection
    )
    if document_retrieved is None:
        # TODO: This is the correct semantics, evaluate impact on client versus some kind of empty response.
        #       Or should initialization of a patient include populating such documents.
        flask.abort(http.HTTPStatus.NOT_FOUND)

    return document_retrieved


@patient_profile_blueprint.route(
    "/<string:patient_id>/patient_profile",
    methods=["PUT"],
)
@validate_schema(patient_profile_schema)
@flask_json.as_json
def put_patient_profile(patient_id):
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
        flask.abort(http.HTTPStatus.NOT_FOUND)

    # Obtain patient collection
    patient_collection = context.database.get_collection(patient_document["collection"])

    # Obtain the document being put
    document = flask.request.json

    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        flask.abort(http.HTTPStatus.BAD_REQUEST)

    # Store the document
    try:
        result = scope.database.patient.patient_profile.put_patient_profile(
            collection=patient_collection,
            patient_profile=document,
        )

        return result.document
    except pymongo.errors.DuplicateKeyError:
        # Indicates a race condition, return error and current revision to client
        document_conflict = scope.database.patient.patient_profile.get_patient_profile(
            collection=patient_collection
        )
        return document_conflict, http.HTTPStatus.CONFLICT
