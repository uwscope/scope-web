import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.mood_logs
import scope.schema

mood_logs_blueprint = flask.Blueprint(
    "mood_logs_blueprint",
    __name__,
)


@mood_logs_blueprint.route(
    "/<string:patient_id>/moodlogs",
    methods=["GET"],
)
@flask_json.as_json
def get_mood_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.mood_logs.get_mood_logs(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "moodlogs": documents,
    }


@mood_logs_blueprint.route(
    "/<string:patient_id>/moodlogs",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.mood_log_schema,
    key="moodlog",
)
@flask_json.as_json
def post_mood_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["moodlog"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.mood_logs.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.mood_logs.post_mood_log(
        collection=patient_collection,
        mood_log=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "moodlog": document_response,
    }


@mood_logs_blueprint.route(
    "/<string:patient_id>/moodlog/<string:moodlog_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_mood_log(patient_id, moodlog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.mood_logs.get_mood_log(
        collection=patient_collection,
        set_id=moodlog_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "moodlog": document,
    }


@mood_logs_blueprint.route(
    "/<string:patient_id>/moodlog/<string:moodlog_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.mood_log_schema,
    key="moodlog",
)
@flask_json.as_json
def put_mood_log(patient_id, moodlog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["moodlog"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.mood_logs.SEMANTIC_SET_ID,
        document=document,
        set_id=moodlog_id,
    )

    # Store the document
    try:
        result = scope.database.patient.mood_logs.put_mood_log(
            collection=patient_collection,
            mood_log=document,
            set_id=moodlog_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.mood_logs.get_mood_log(
            collection=patient_collection, set_id=moodlog_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "moodlog": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "moodlog": document_response,
        }
