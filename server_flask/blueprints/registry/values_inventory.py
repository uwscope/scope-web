import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.values_inventory
import scope.schema

values_inventory_blueprint = flask.Blueprint(
    "values_inventory_blueprint",
    __name__,
)


@values_inventory_blueprint.route(
    "/<string:patient_id>/valuesinventory",
    methods=["GET"],
)
@flask_json.as_json
def get_values_inventory(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.values_inventory.get_values_inventory(
        collection=patient_collection,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "valuesinventory": document,
    }


@values_inventory_blueprint.route(
    "/<string:patient_id>/valuesinventory",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.values_inventory_schema,
    key="valuesinventory",
)
@flask_json.as_json
def put_values_inventory(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["valuesinventory"]

    # Validate and normalize the request
    document = request_utils.singleton_put_request_validate(
        document=document,
    )

    # Store the document
    try:
        result = scope.database.patient.values_inventory.put_values_inventory(
            collection=patient_collection,
            values_inventory=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.values_inventory.get_values_inventory(
                collection=patient_collection
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "valuesinventory": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )
        return {
            "valuesinventory": document_response,
        }
