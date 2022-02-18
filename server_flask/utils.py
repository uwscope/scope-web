import flask
import functools
import http
import json
import jschon


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
