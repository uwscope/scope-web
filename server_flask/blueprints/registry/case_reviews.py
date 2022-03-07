import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.case_reviews
import scope.schema

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
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.case_reviews.get_case_reviews(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "casereviews": documents,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereviews",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.case_review_schema,
    key="casereview",
)
@flask_json.as_json
def post_case_review(patient_id):
    """
    Creates a new case review in the patient record and returns the case review result.
    """
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["casereview"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.case_reviews.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.case_reviews.post_case_review(
        collection=patient_collection,
        case_review=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "casereview": document_response,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereview/<string:casereview_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_case_review(patient_id, casereview_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.case_reviews.get_case_review(
        collection=patient_collection,
        set_id=casereview_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "casereview": document,
    }


@case_reviews_blueprint.route(
    "/<string:patient_id>/casereview/<string:casereview_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.case_review_schema,
    key="casereview",
)
@flask_json.as_json
def put_case_review(patient_id, casereview_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["casereview"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.case_reviews.SEMANTIC_SET_ID,
        document=document,
        set_id=casereview_id,
    )

    # Store the document
    try:
        result = scope.database.patient.case_reviews.put_case_review(
            collection=patient_collection,
            case_review=document,
            set_id=casereview_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.case_reviews.get_case_review(
            collection=patient_collection, set_id=casereview_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "casereview": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "casereview": document_response,
        }
