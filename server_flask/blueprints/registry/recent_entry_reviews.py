import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.recent_entry_reviews
import scope.schema

recent_entry_reviews_blueprint = flask.Blueprint(
    "recent_entry_reviews_blueprint",
    __name__,
)


@recent_entry_reviews_blueprint.route(
    "/<string:patient_id>/recententryreviews",
    methods=["GET"],
)
@flask_json.as_json
def get_recent_entry_reviews(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.recent_entry_reviews.get_recent_entry_reviews(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "recententryreviews": documents,
    }


@recent_entry_reviews_blueprint.route(
    "/<string:patient_id>/recententryreviews",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.recent_entry_review_schema,
    key="recententryreview",
)
@flask_json.as_json
def post_recent_entry_reviews(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["recententryreview"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.recent_entry_reviews.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.recent_entry_reviews.post_recent_entry_review(
        collection=patient_collection,
        recent_entry_review=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "recententryreview": document_response,
    }


@recent_entry_reviews_blueprint.route(
    "/<string:patient_id>/recententryreview/<string:recententryreview_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_recent_entry_review(patient_id, recententryreview_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.recent_entry_reviews.get_recent_entry_review(
        collection=patient_collection,
        set_id=recententryreview_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "recententryreview": document,
    }


@recent_entry_reviews_blueprint.route(
    "/<string:patient_id>/recententryreview/<string:recententryreview_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.recent_entry_review_schema,
    key="recententryreview",
)
@flask_json.as_json
def put_recent_entry_review(patient_id, recententryreview_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["recententryreview"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.recent_entry_reviews.SEMANTIC_SET_ID,
        document=document,
        set_id=recententryreview_id,
    )

    # Store the document
    try:
        result = scope.database.patient.recent_entry_reviews.put_recent_entry_review(
            collection=patient_collection,
            recent_entry_review=document,
            set_id=recententryreview_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = (
            scope.database.patient.recent_entry_reviews.get_recent_entry_review(
                collection=patient_collection, set_id=recententryreview_id
            )
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "recententryreview": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "recententryreview": document_response,
        }
