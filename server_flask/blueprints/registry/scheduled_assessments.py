import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.scheduled_assessments
import scope.schema

scheduled_assessments_blueprint = flask.Blueprint(
    "scheduled_assessments_blueprint",
    __name__,
)


@scheduled_assessments_blueprint.route(
    "/<string:patient_id>/scheduledassessments",
    methods=["GET"],
)
@flask_json.as_json
def get_scheduled_assessments(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.scheduled_assessments.get_scheduled_assessments(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "scheduledassessments": documents,
    }


@scheduled_assessments_blueprint.route(
    "/<string:patient_id>/scheduledassessments",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.scheduled_assessment_schema,
    key="scheduledassessment",
)
@flask_json.as_json
def post_scheduled_assessments(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["scheduledassessment"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.scheduled_assessments.post_scheduled_assessment(
        collection=patient_collection,
        scheduled_assessment=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "scheduledassessment": document_response,
    }


@scheduled_assessments_blueprint.route(
    "/<string:patient_id>/scheduledassessment/<string:scheduleassessment_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_scheduled_assessment(patient_id, scheduleassessment_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.scheduled_assessments.get_scheduled_assessment(
        collection=patient_collection,
        set_id=scheduleassessment_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "scheduledassessment": document,
    }


@scheduled_assessments_blueprint.route(
    "/<string:patient_id>/scheduledassessment/<string:scheduleassessment_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.scheduled_assessment_schema,
    key="scheduledassessment",
)
@flask_json.as_json
def put_scheduled_assessment(patient_id, scheduleassessment_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["scheduledassessment"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID,
        document=document,
        set_id=scheduleassessment_id,
    )

    # Store the document
    try:
        result = scope.database.patient.scheduled_assessments.put_scheduled_assessment(
            collection=patient_collection,
            scheduled_assessment=document,
            set_id=scheduleassessment_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.scheduled_assessments.get_scheduled_assessment(
                collection=patient_collection, set_id=scheduleassessment_id
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "scheduledassessment": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "scheduledassessment": document_response,
        }
