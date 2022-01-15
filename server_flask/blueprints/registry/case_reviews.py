import http
from functools import wraps

import scope.database
import scope.database.case_reviews
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import case_review_schema
from utils import validate_schema

registry_case_reviews_blueprint = Blueprint(
    "registry_case_reviews_blueprint", __name__, url_prefix="/patients"
)


@registry_case_reviews_blueprint.route(
    "/<string:patient_collection>/casereviews", methods=["GET"]
)
@as_json
def get_case_reviews(patient_collection):
    context = request_context()

    result = scope.database.case_reviews.get_case_reviews(
        database=context.database, collection_name=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_case_reviews_blueprint.route(
    "/<string:patient_collection>/casereviews", methods=["POST"]
)
@validate_schema(case_review_schema)
@as_json
def create_case_review(patient_collection):
    """
    Adds a new case review in the patient record and returns the case review.
    """

    case_review = request.json

    if "_id" in case_review:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    context = request_context()

    result = scope.database.case_reviews.create_case_review(
        database=context.database,
        collection_name=patient_collection,
        case_review=case_review,
    )

    if result is not None:
        case_review.update({"_id": str(result.inserted_id)})
        return case_review, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422


@registry_case_reviews_blueprint.route(
    "/<string:patient_collection>/casereviews/<string:review_id>", methods=["GET"]
)
@as_json
def get_case_review(patient_collection, review_id):
    context = request_context()

    result = scope.database.case_reviews.get_case_review(
        database=context.database,
        collection_name=patient_collection,
        review_id=review_id,
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_case_reviews_blueprint.route(
    "/<string:patient_collection>/casereviews/<string:review_id>", methods=["PUT"]
)
@validate_schema(case_review_schema)
@as_json
def update_case_review(patient_collection, review_id):

    case_review = request.json

    if "_id" in case_review:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    case_review["_rev"] += 1

    # NOTE: Assume client is not sending review_id as part of json.
    case_review.update({"_review_id": review_id})

    context = request_context()

    result = scope.database.case_reviews.update_case_review(
        database=context.database,
        collection_name=patient_collection,
        case_review=case_review,
    )

    if result is not None:
        case_review.update({"_id": str(result.inserted_id)})
        return case_review, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
