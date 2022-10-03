import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.activity_schedules
import scope.schema

activity_schedules_blueprint = flask.Blueprint(
    "activity_schedules_blueprint",
    __name__,
)


@activity_schedules_blueprint.route(
    "/<string:patient_id>/activityschedules",
    methods=["GET"],
)
@flask_json.as_json
def get_activity_schedules(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.activity_schedules.get_activity_schedules(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "activityschedules": documents,
    }


@activity_schedules_blueprint.route(
    "/<string:patient_id>/activityschedules",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_schedule_schema,
    key="activityschedule",
)
@flask_json.as_json
def post_activity_schedules(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activityschedule"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.activity_schedules.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.activity_schedules.post_activity_schedule(
        collection=patient_collection,
        activity_schedule=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "activityschedule": document_response,
    }


@activity_schedules_blueprint.route(
    "/<string:patient_id>/activityschedule/<string:activityschedule_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_activity_schedule(patient_id, activityschedule_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.activity_schedules.get_activity_schedule(
        collection=patient_collection,
        set_id=activityschedule_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "activityschedule": document,
    }


@activity_schedules_blueprint.route(
    "/<string:patient_id>/activityschedule/<string:activityschedule_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_schedule_schema,
    key="activityschedule",
)
@flask_json.as_json
def put_activity_schedule(patient_id, activityschedule_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activityschedule"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.activity_schedules.SEMANTIC_SET_ID,
        document=document,
        set_id=activityschedule_id,
    )

    # Store the document
    try:
        result = scope.database.patient.activity_schedules.put_activity_schedule(
            collection=patient_collection,
            activity_schedule=document,
            set_id=activityschedule_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.activity_schedules.get_activity_schedule(
                collection=patient_collection, set_id=activityschedule_id
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "activityschedule": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "activityschedule": document_response,
        }
