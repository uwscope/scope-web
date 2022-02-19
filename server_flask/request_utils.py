import flask
import functools
import http
import jschon
from typing import NoReturn


def _flask_abort(response: dict, status: int) -> NoReturn:
    flask.abort(
        flask.make_response(
            flask.jsonify(response),
            status,
        )
    )


def abort_document_not_found() -> NoReturn:
    _flask_abort(
        {
            "message": "Document not found.",
        },
        http.HTTPStatus.NOT_FOUND,
    )


def abort_patient_not_found() -> NoReturn:
    _flask_abort(
        {
            "message": "Patient not found.",
        },
        http.HTTPStatus.NOT_FOUND,
    )


def abort_post_with_id() -> NoReturn:
    _flask_abort(
        {
            "message": 'POST must not include "_id".',
        },
        http.HTTPStatus.BAD_REQUEST,
    )


def abort_post_with_set_id() -> NoReturn:
    _flask_abort(
        {
            "message": 'POST must not include "_set_id".',
        },
        http.HTTPStatus.BAD_REQUEST,
    )


def abort_post_with_rev() -> NoReturn:
    _flask_abort(
        {
            "message": 'POST must not include "_rev".',
        },
        http.HTTPStatus.BAD_REQUEST,
    )


def abort_put_with_id() -> NoReturn:
    _flask_abort(
        {
            "message": 'PUT must not include "_id".',
        },
        http.HTTPStatus.BAD_REQUEST,
    )


def abort_put_with_mismatched_setid() -> NoReturn:
    _flask_abort(
        {
            "message": 'PUT location must match "_set_id".',
        },
        http.HTTPStatus.BAD_REQUEST,
    )


def abort_revision_conflict(*, document: dict) -> NoReturn:
    _flask_abort(
        document
        | {
            "message": "Revision conflict.",
        },
        http.HTTPStatus.CONFLICT,
    )


def singleton_get_response_validate(*, document: dict) -> dict:
    # If database get found None, return a 404
    if document is None:
        abort_document_not_found()

    return document


def singleton_put_request_validate(*, document: dict) -> dict:
    # Previously stored documents contain an "_id",
    # documents to be put must not already contain an "_id"
    if "_id" in document:
        abort_put_with_id()

    return document


def singleton_put_response_validate(*, document: dict) -> dict:
    return document


def validate_schema(
    *,
    schema: jschon.JSONSchema,
    key: str = None,
):
    """
    Validate a schema against the request body.
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Body JSON
            document = flask.request.json

            if key:
                if key not in document:
                    flask.abort(
                        flask.make_response(
                            flask.jsonify(
                                {
                                    "message": 'Schema validation failed, key not found "{}".'.format(
                                        key
                                    ),
                                    "request": flask.request.json,
                                }
                            ),
                            http.HTTPStatus.BAD_REQUEST,
                        )
                    )

                document = document[key]

            # Argument needs to be of type jschon.json.JSON
            result = schema.evaluate(jschon.JSON(document))

            if not result.output("flag")["valid"]:
                flask.abort(
                    flask.make_response(
                        flask.jsonify(
                            {
                                "message": "Schema validation failed.",
                                "error": result.output("detailed"),
                                "request": flask.request.json,
                            }
                        ),
                        http.HTTPStatus.BAD_REQUEST,
                    )
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator
