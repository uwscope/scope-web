import flask
import flask_json
import pymongo.errors
import scope.database
import scope.database.patient.sessions
from request_context import request_context
from scope.schema import session_schema
from utils import validate_schema

sessions_blueprint = flask.Blueprint(
    "sessions_blueprint",
    __name__,
)


@sessions_blueprint.route(
    "/<string:patient_id>/sessions",
    methods=["GET"],
)
@flask_json.as_json
def get_sessions(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.sessions.get_sessions(
        collection=patient_collection,
    )
    if documents is None:
        return {
            "sessions": [],
        }

    return {
        "sessions": documents,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/sessions",
    methods=["POST"],
)
@validate_schema(
    schema=session_schema,
    key="session",
)
@flask_json.as_json
def post_session(patient_id):
    """
    Creates a new session in the patient record and returns the session.
    """

    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["session"]

    # Previously stored documents contain an "_id",
    # documents to be post must not already contain an "_id"
    if "_id" in document:
        context.abort_post_with_id()

    # Previously stored documents contain a "_set_id",
    # documents to be post must not already contain an "_set_id"
    if "_set_id" in document:
        context.abort_post_with_set_id()

    # Previously stored documents contain an "_rev",
    # documents to be post must not already contain a "_rev"
    if "_rev" in document:
        context.abort_post_with_rev()

    # Store the document
    result = scope.database.patient.sessions.post_session(
        collection=patient_collection,
        session=document,
    )

    return {
        "session": result.document,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/session/<string:session_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_session(patient_id, session_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.sessions.get_session(
        collection=patient_collection,
        set_id=session_id,
    )
    if document is None:
        context.abort_document_not_found()

    return {
        "session": document,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/session/<string:session_id>",
    methods=["PUT"],
)
@validate_schema(
    schema=session_schema,
    key="session",
)
@flask_json.as_json
def put_session(patient_id, session_id):

    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["session"]

    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        context.abort_put_with_id()

    # Store the document
    try:
        result = scope.database.patient.sessions.put_session(
            collection=patient_collection,
            session=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.sessions.get_session(
            collection=patient_collection, set_id=session_id
        )
        context.abort_revision_conflict(
            document={
                "session": document_conflict,
            }
        )
    else:
        return {
            "session": result.document,
        }
