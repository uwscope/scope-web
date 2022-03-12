import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.sessions
import scope.schema

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
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.sessions.get_sessions(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "sessions": documents,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/sessions",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.session_schema,
    key="session",
)
@flask_json.as_json
def post_session(patient_id):
    """
    Creates and return a new session.
    """

    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["session"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.sessions.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.sessions.post_session(
        collection=patient_collection,
        session=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "session": document_response,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/session/<string:session_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_session(patient_id, session_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.sessions.get_session(
        collection=patient_collection,
        set_id=session_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "session": document,
    }


@sessions_blueprint.route(
    "/<string:patient_id>/session/<string:session_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.session_schema,
    key="session",
)
@flask_json.as_json
def put_session(patient_id, session_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["session"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.sessions.SEMANTIC_SET_ID,
        document=document,
        set_id=session_id,
    )

    # Store the document
    try:
        result = scope.database.patient.sessions.put_session(
            collection=patient_collection,
            session=document,
            set_id=session_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.sessions.get_session(
            collection=patient_collection, set_id=session_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "session": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "session": document_response,
        }
