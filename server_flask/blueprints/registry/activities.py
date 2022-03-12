import flask
import flask_json
import pymongo.errors
import request_context

import request_utils
import scope.database
import scope.database.patient.activities
import scope.schema

activities_blueprint = flask.Blueprint(
    "activities_blueprint",
    __name__,
)


@activities_blueprint.route(
    "/<string:patient_id>/activities",
    methods=["GET"],
)
@flask_json.as_json
def get_activities(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.activities.get_activities(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "activities": documents,
    }


@activities_blueprint.route(
    "/<string:patient_id>/activities",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_schema,
    key="activity",
)
@flask_json.as_json
def post_activities(patient_id):
    """
    Creates a new activity in the patient record and returns the activity result.
    """

    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activity"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.activities.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.activities.post_activity(
        collection=patient_collection,
        activity=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "activity": document_response,
    }


@activities_blueprint.route(
    "/<string:patient_id>/activity/<string:activity_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_activity(patient_id, activity_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.activities.get_activity(
        collection=patient_collection,
        set_id=activity_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "activity": document,
    }


@activities_blueprint.route(
    "/<string:patient_id>/activity/<string:activity_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.activity_schema,
    key="activity",
)
@flask_json.as_json
def put_activity(patient_id, activity_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["activity"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.activities.SEMANTIC_SET_ID,
        document=document,
        set_id=activity_id,
    )

    # Store the document
    try:
        result = scope.database.patient.activities.put_activity(
            collection=patient_collection,
            activity=document,
            set_id=activity_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.activities.get_activity(
            collection=patient_collection, set_id=activity_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "activity": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "activity": document_response,
        }
