import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
from scope.database import collection_utils
import scope.database.patient.push_subscriptions
import scope.schema

push_subscriptions_blueprint = flask.Blueprint(
    "push_subscriptions_blueprint",
    __name__,
)


@push_subscriptions_blueprint.route(
    "/<string:patient_id>/pushsubscriptions",
    methods=["GET"],
)
@flask_json.as_json
def get_push_subscriptions(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.push_subscriptions.get_push_subscriptions(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "pushsubscriptions": documents,
    }


@push_subscriptions_blueprint.route(
    "/<string:patient_id>/pushsubscriptions",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.push_subscription_schema,
    key="pushsubscription",
)
@flask_json.as_json
def post_push_subscriptions(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["pushsubscription"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.push_subscriptions.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.push_subscriptions.post_push_subscription(
        collection=patient_collection,
        push_subscription=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "pushsubscription": document_response,
    }


@push_subscriptions_blueprint.route(
    "/<string:patient_id>/pushsubscription/<string:pushsubscription_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_push_subscription(patient_id, pushsubscription_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.push_subscriptions.get_push_subscription(
        collection=patient_collection,
        set_id=pushsubscription_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "pushsubscription": document,
    }


@push_subscriptions_blueprint.route(
    "/<string:patient_id>/pushsubscription/<string:pushsubscription_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.push_subscription_schema,
    key="pushsubscription",
)
@flask_json.as_json
def put_push_subscription(patient_id, pushsubscription_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["pushsubscription"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.push_subscriptions.SEMANTIC_SET_ID,
        document=document,
        set_id=pushsubscription_id,
    )

    # Store the document
    try:
        result = scope.database.patient.push_subscriptions.put_push_subscription(
            collection=patient_collection,
            push_subscription=document,
            set_id=pushsubscription_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.push_subscriptions.get_push_subscription(
                collection=patient_collection, set_id=pushsubscription_id
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "pushsubscription": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "pushsubscription": document_response,
        }


@push_subscriptions_blueprint.route(
    "/<string:patient_id>/pushsubscription/<string:pushsubscription_id>",
    methods=["DELETE"],
)
@flask_json.as_json
def delete_push_subscription(patient_id, pushsubscription_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the _rev being deleted
    if_match_header = flask.request.headers.get("If-Match")
    if if_match_header is None:
        request_utils.abort_delete_without_if_match_header()
    rev = int(if_match_header)

    # Delete the document
    try:
        result = scope.database.patient.push_subscriptions.delete_push_subscription(
            collection=patient_collection,
            set_id=pushsubscription_id,
            rev=rev,
        )
    except collection_utils.DocumentNotFoundException:
        # The document may have never existed or may have already been deleted
        request_utils.abort_document_not_found()
    except collection_utils.DocumentModifiedException as e:
        # Indicates a revision race condition, return error with current revision
        document_existing = e.document_existing

        request_utils.abort_revision_conflict(
            document={
                "pushsubscription": document_existing,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "pushsubscription": document_response,
        }
