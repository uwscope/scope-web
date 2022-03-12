import flask
import flask_json
import pymongo.errors
import scope.database
import scope.database.patient.assessment_logs

import request_context
import request_utils
import scope.schema

assessment_logs_blueprint = flask.Blueprint(
    "assessment_logs_blueprint",
    __name__,
)


@assessment_logs_blueprint.route(
    "/<string:patient_id>/assessmentlogs",
    methods=["GET"],
)
@flask_json.as_json
def get_assessment_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.assessment_logs.get_assessment_logs(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "assessmentlogs": documents,
    }


@assessment_logs_blueprint.route(
    "/<string:patient_id>/assessmentlogs",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.assessment_log_schema,
    key="assessmentlog",
)
@flask_json.as_json
def post_assessment_logs(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["assessmentlog"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.assessment_logs.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.assessment_logs.post_assessment_log(
        collection=patient_collection,
        assessment_log=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "assessmentlog": document_response,
    }


@assessment_logs_blueprint.route(
    "/<string:patient_id>/assessmentlog/<string:assessmentlog_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_assessment_log(patient_id, assessmentlog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.assessment_logs.get_assessment_log(
        collection=patient_collection,
        set_id=assessmentlog_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "assessmentlog": document,
    }


@assessment_logs_blueprint.route(
    "/<string:patient_id>/assessmentlog/<string:assessmentlog_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.assessment_log_schema,
    key="assessmentlog",
)
@flask_json.as_json
def put_assessment_log(patient_id, assessmentlog_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["assessmentlog"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.assessment_logs.SEMANTIC_SET_ID,
        document=document,
        set_id=assessmentlog_id,
    )

    # Store the document
    try:
        result = scope.database.patient.assessment_logs.put_assessment_log(
            collection=patient_collection,
            assessment_log=document,
            set_id=assessmentlog_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.assessment_logs.get_assessment_log(
            collection=patient_collection, set_id=assessmentlog_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "assessmentlog": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "assessmentlog": document_response,
        }
