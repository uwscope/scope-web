import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.patient_profile
import scope.database.patients
import scope.schema

patient_profile_blueprint = flask.Blueprint(
    "patient_profile_blueprint",
    __name__,
)


@patient_profile_blueprint.route(
    "/<string:patient_id>/profile",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_profile(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "profile": document,
    }


@patient_profile_blueprint.route(
    "/<string:patient_id>/profile",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.patient_profile_schema,
    key="profile",
)
@flask_json.as_json
def put_patient_profile(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["profile"]

    # Validate and normalize the request
    document = request_utils.singleton_put_request_validate(
        document=document,
    )

    # Store the document
    try:
        result = scope.database.patient.patient_profile.put_patient_profile(
            database=context.database,
            collection=patient_collection,
            patient_id=patient_id,
            patient_profile=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.patient_profile.get_patient_profile(
            collection=patient_collection
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "profile": document_conflict,
            }
        )
    else:
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )
        return {
            "profile": document_response,
        }
