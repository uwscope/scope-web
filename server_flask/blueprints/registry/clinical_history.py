import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.clinical_history
import scope.schema

clinical_history_blueprint = flask.Blueprint("clinical_history_blueprint", __name__)


@clinical_history_blueprint.route(
    "/<string:patient_id>/clinicalhistory",
    methods=["GET"],
)
@flask_json.as_json
def get_clinical_history(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.clinical_history.get_clinical_history(
        collection=patient_collection,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "clinicalhistory": document,
    }


@clinical_history_blueprint.route(
    "/<string:patient_id>/clinicalhistory",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.clinical_history_schema,
    key="clinicalhistory",
)
@flask_json.as_json
def put_clinical_history(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["clinicalhistory"]

    # Validate and normalize the request
    document = request_utils.singleton_put_request_validate(
        document=document,
    )

    # Store the document
    try:
        result = scope.database.patient.clinical_history.put_clinical_history(
            collection=patient_collection,
            clinical_history=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.clinical_history.get_clinical_history(
                collection=patient_collection
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "clinicalhistory": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "clinicalhistory": document_response,
        }
