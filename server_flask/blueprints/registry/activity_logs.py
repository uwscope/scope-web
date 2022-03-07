import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.activity_logs
import scope.schema

activity_logs_blueprint = flask.Blueprint(
    "activity_logs_blueprint",
    __name__,
)


@activity_logs_blueprint.route(
    "/<string:patient_id>/activitylogs",
    methods=["GET"],
)
@flask_json.as_json
def get_activity_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.activity_logs.get_activity_logs(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "activitylogs": documents,
    }


@activity_logs_blueprint.route(
    "/<string:patient_id>/activitylogs",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_log_schema,
    key="activitylog",
)
@flask_json.as_json
def post_activity_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activitylog"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.activity_logs.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.activity_logs.post_activity_log(
        collection=patient_collection,
        activity_log=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "activitylog": document_response,
    }


@activity_logs_blueprint.route(
    "/<string:patient_id>/activitylog/<string:activitylog_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_activity_log(patient_id, activitylog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.activity_logs.get_activity_log(
        collection=patient_collection,
        set_id=activitylog_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "activitylog": document,
    }


@activity_logs_blueprint.route(
    "/<string:patient_id>/activitylog/<string:activitylog_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_log_schema,
    key="activitylog",
)
@flask_json.as_json
def put_activity_log(patient_id, activitylog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activitylog"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.activity_logs.SEMANTIC_SET_ID,
        document=document,
        set_id=activitylog_id,
    )

    # Store the document
    try:
        result = scope.database.patient.activity_logs.put_activity_log(
            collection=patient_collection,
            activity_log=document,
            set_id=activitylog_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.activity_logs.get_activity_log(
            collection=patient_collection, set_id=activitylog_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "activitylog": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "activitylog": document_response,
        }
