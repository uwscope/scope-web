import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.scheduled_activities
import scope.schema

scheduled_activities_blueprint = flask.Blueprint(
    "scheduled_activities_blueprint",
    __name__,
)


@scheduled_activities_blueprint.route(
    "/<string:patient_id>/scheduledactivities",
    methods=["GET"],
)
@flask_json.as_json
def get_scheduled_activities(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.scheduled_activities.get_scheduled_activities(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "scheduledactivities": documents,
    }


@scheduled_activities_blueprint.route(
    "/<string:patient_id>/scheduledactivities",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.scheduled_activity_schema,
    key="scheduledactivity",
)
@flask_json.as_json
def post_scheduled_activities(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["scheduledactivity"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.scheduled_activities.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.scheduled_activities.post_scheduled_activity(
        collection=patient_collection,
        scheduled_activity=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "scheduledactivity": document_response,
    }


@scheduled_activities_blueprint.route(
    "/<string:patient_id>/scheduledactivity/<string:scheduleactivity_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_scheduled_activity(patient_id, scheduleactivity_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.scheduled_activities.get_scheduled_activity(
        collection=patient_collection,
        set_id=scheduleactivity_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "scheduledactivity": document,
    }


@scheduled_activities_blueprint.route(
    "/<string:patient_id>/scheduledactivity/<string:scheduleactivity_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.scheduled_activity_schema,
    key="scheduledactivity",
)
@flask_json.as_json
def put_scheduled_activity(patient_id, scheduleactivity_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["scheduledactivity"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.scheduled_activities.SEMANTIC_SET_ID,
        document=document,
        set_id=scheduleactivity_id,
    )

    # Store the document
    try:
        result = scope.database.patient.scheduled_activities.put_scheduled_activity(
            collection=patient_collection,
            scheduled_activity=document,
            set_id=scheduleactivity_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.scheduled_activities.get_scheduled_activity(
                collection=patient_collection, set_id=scheduleactivity_id
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "scheduledactivity": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "scheduledactivity": document_response,
        }
