import flask
import flask_json
import pymongo.errors

import request_context
import request_utils
import scope.database
import scope.database.patient.review_marks
import scope.schema

review_marks_blueprint = flask.Blueprint(
    "review_marks_blueprint",
    __name__,
)


@review_marks_blueprint.route(
    "/<string:patient_id>/reviewmarks",
    methods=["GET"],
)
@flask_json.as_json
def get_review_marks(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    documents = scope.database.patient.review_marks.get_review_marks(
        collection=patient_collection,
    )

    # Validate and normalize the response
    documents = request_utils.set_get_response_validate(
        documents=documents,
    )

    return {
        "reviewmarks": documents,
    }


@review_marks_blueprint.route(
    "/<string:patient_id>/reviewmarks",
    methods=["POST"],
)
@request_utils.validate_schema(
    schema=scope.schema.review_mark_schema,
    key="reviewmark",
)
@flask_json.as_json
def post_review_marks(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["reviewmark"]

    # Validate and normalize the request
    document = request_utils.set_post_request_validate(
        semantic_set_id=scope.database.patient.review_marks.SEMANTIC_SET_ID,
        document=document,
    )

    # Store the document
    result = scope.database.patient.review_marks.post_review_mark(
        collection=patient_collection,
        review_mark=document,
    )

    # Validate and normalize the response
    document_response = request_utils.set_post_response_validate(
        document=result.document,
    )

    return {
        "reviewmark": document_response,
    }


@review_marks_blueprint.route(
    "/<string:patient_id>/reviewmark/<string:reviewmark_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_review_mark(patient_id, reviewmark_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Get the document
    document = scope.database.patient.review_marks.get_review_mark(
        collection=patient_collection,
        set_id=reviewmark_id,
    )

    # Validate and normalize the response
    document = request_utils.singleton_get_response_validate(
        document=document,
    )

    return {
        "reviewmark": document,
    }


@review_marks_blueprint.route(
    "/<string:patient_id>/reviewmark/<string:reviewmark_id>",
    methods=["PUT"],
)
@request_utils.validate_schema(
    schema=scope.schema.review_mark_schema,
    key="reviewmark",
)
@flask_json.as_json
def put_review_mark(patient_id, reviewmark_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    patient_collection = context.patient_collection(patient_id=patient_id)

    # Obtain the document being put
    document = flask.request.json["reviewmark"]

    # Validate and normalize the request
    document = request_utils.set_element_put_request_validate(
        semantic_set_id=scope.database.patient.review_marks.SEMANTIC_SET_ID,
        document=document,
        set_id=reviewmark_id,
    )

    # Store the document
    try:
        result = scope.database.patient.review_marks.put_review_mark(
            collection=patient_collection,
            review_mark=document,
            set_id=reviewmark_id,
        )
    except pymongo.errors.DuplicateKeyError:
        # Indicates a revision race condition, return error with current revision
        document_conflict = scope.database.patient.review_marks.get_review_mark(
            collection=patient_collection, set_id=reviewmark_id
        )
        # Validate and normalize the response
        document_conflict = request_utils.singleton_put_response_validate(
            document=document_conflict
        )

        request_utils.abort_revision_conflict(
            document={
                "reviewmark": document_conflict,
            }
        )
    else:
        # Validate and normalize the response
        document_response = request_utils.singleton_put_response_validate(
            document=result.document,
        )

        return {
            "reviewmark": document_response,
        }
