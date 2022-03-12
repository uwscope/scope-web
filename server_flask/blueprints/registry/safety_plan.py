import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.safety_plan
import scope.schema

safety_plan_blueprint = flask.Blueprint(
    "safety_plan_blueprint",
    __name__,
)


@safety_plan_blueprint.route(
    "/<string:patient_id>/safetyplan",
    methods=["GET"],
)
@flask_json.as_json
def get_safety_plan(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "safetyplan": document,
    }


@safety_plan_blueprint.route(
    "/<string:patient_id>/safetyplan",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.safety_plan_schema,
    key="safetyplan",
)
@flask_json.as_json
def put_safety_plan(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["safetyplan"]

    # Validate and normalize the request
    document = request_utils.singleton_put_request_validate(
        document=document,
    )

    # Store the document
    try:
        result = scope.database.patient.safety_plan.put_safety_plan(
            collection=patient_collection,
            safety_plan=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.safety_plan.get_safety_plan(
            collection=patient_collection
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "safetyplan": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )
        return {
            "safetyplan": document_response,
        }
