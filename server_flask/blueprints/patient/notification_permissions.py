import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.notification_permissions
import scope.schema

notification_permissions_blueprint = flask.Blueprint(
    "notification_permissions_blueprint", __name__
)


@notification_permissions_blueprint.route(
    "/<string:patient_id>/notificationpermissions",
    methods=["GET"],
)
@flask_json.as_json
def get_notification_permissions(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = (
        scope.database.patient.notification_permissions.get_notification_permissions(
            collection=patient_collection,
        )
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "notificationpermissions": document,
    }


@notification_permissions_blueprint.route(
    "/<string:patient_id>/notificationpermissions",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.notification_permissions_schema,
    key="notificationpermissions",
)
@flask_json.as_json
def put_notification_permissions(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["notificationpermissions"]

    # Validate and normalize the request
    document = request_utils.singleton_put_request_validate(
        document=document,
    )

    # Store the document
    try:
        result = scope.database.patient.notification_permissions.put_notification_permissions(
            collection=patient_collection,
            notification_permissions=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.notification_permissions.get_notification_permissions(
            collection=patient_collection
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "notificationpermissions": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "notificationpermissions": document_response,
        }
