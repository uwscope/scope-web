import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.values
import scope.schema

values_blueprint = flask.Blueprint(
    "values_blueprint",
    __name__,
)


@values_blueprint.route(
    "/<string:patient_id>/values",
    methods=["GET"],
)
@flask_json.as_json
def get_values(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.values.get_values(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "values": documents,
    }


@values_blueprint.route(
    "/<string:patient_id>/values",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.value_schema,
    key="value",
)
@flask_json.as_json
def post_value(patient_id):
    """
    Creates and return a new value.
    """

    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["value"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.values.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.values.post_value(
        collection=patient_collection,
        value=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "value": document_response,
    }


@values_blueprint.route(
    "/<string:patient_id>/value/<string:value_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_value(patient_id, value_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.values.get_value(
        collection=patient_collection,
        set_id=value_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "value": document,
    }


@values_blueprint.route(
    "/<string:patient_id>/value/<string:value_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.value_schema,
    key="value",
)
@flask_json.as_json
def put_value(patient_id, value_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["value"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.values.SEMANTIC_SET_ID,
        document=document,
        set_id=value_id,
    )

    # Store the document
    try:
        result = scope.database.patient.values.put_value(
            collection=patient_collection,
            value=document,
            set_id=value_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.values.get_value(
            collection=patient_collection, set_id=value_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "value": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "value": document_response,
        }


@values_blueprint.route(
    "/<string:patient_id>/value/<string:value_id>",
    methods=["DELETE"],
)
@flask_json.as_json
def delete_value(patient_id, value_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    if_match_header = flask.request.headers.get("If-Match")
    if if_match_header is None:
        request_utils.abort_delete_without_if_match_header()

    # Delete the document
    try:
        result = scope.database.patient.values.delete_value(
            collection=patient_collection, set_id=value_id, rev=int(if_match_header)
        )
    except pymongo.errors.DuplicateKeyError:
        # NOTE: Possible reasons to arrive here:
        # (1): document with (_rev == if_match_header + 1) already exists in which case current "value" document will be returned with 409.
        # (2): deleted document with (_rev == if_match_header + 1) already exists in which case null "value" document will be returned with 409.

        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.values.get_value(
            collection=patient_collection, set_id=value_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "value": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "value": document_response,
        }
