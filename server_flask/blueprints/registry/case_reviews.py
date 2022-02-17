import flask
import flask_json
import pymongo.errors
import scope.database
import scope.database.patient.case_reviews
from request_context import request_context
from scope.schema import case_review_schema
from utils import validate_schema

case_reviews_blueprint = flask.Blueprint(
    "case_reviews_blueprint",
    __name__,
)


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereviews",
    methods=["GET"],
)
@flask_json.as_json
def get_case_reviews(patient_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.case_reviews.get_case_reviews(
        collection=patient_collection,
    )
    if documents is None:
        return {
            "casereviews": [],
        }

    return {
        "casereviews": documents,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereviews",
    methods=["POST"],
)
@validate_schema(
    schema=case_review_schema,
    key="casereview",
)
@flask_json.as_json
def post_case_reviews(patient_id):
    """
    Creates a new case review in the patient record and returns the case review result.
    """
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["casereview"]

    # Previously stored documents contain an "_id",
    # documents to be post must not already contain an "_id"
    if "_id" in document:
        context.abort_post_with_id()

    # Previously stored documents contain a "_set_id",
    # documents to be post must not already contain an "_set_id"
    if "_set_id" in document:
        context.abort_post_with_set_id()

    # Previously stored documents contain an "_rev",
    # documents to be post must not already contain a "_rev"
    if "_rev" in document:
        context.abort_post_with_rev()

    # Store the document
    result = scope.database.patient.case_reviews.post_case_review(
        collection=patient_collection,
        case_review=document,
    )

    return {
        "casereview": result.document,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereview/<string:review_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_case_review(patient_id, review_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    document = scope.database.patient.case_reviews.get_case_review(
        collection=patient_collection,
        set_id=review_id,
    )
    if document is None:
        context.abort_document_not_found()

    return {
        "casereview": document,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereview/<string:review_id>",
    methods=["PUT"],
)
@validate_schema(
    schema=case_review_schema,
    key="casereview",
)
@flask_json.as_json
def put_case_review(patient_id, review_id):
    # TODO: Require authentication

    context = request_context()
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["casereview"]

    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        context.abort_put_with_id()

    # Store the document
    try:
        result = scope.database.patient.case_reviews.put_case_review(
            collection=patient_collection,
            case_review=document,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.case_reviews.get_case_review(
            collection=patient_collection, set_id=review_id
        )
        context.abort_revision_conflict(
            document={
                "casereview": document_conflict,
            }
        )
    else:
        return {
            "casereview": result.document,
        }
