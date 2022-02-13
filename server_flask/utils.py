import flask
import functools
import http
import json
import jschon


# TODO: Confirm location of the function with James.


def validate_schema(schema_object):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # For .evaluate to work, its argument needs to be of type '<class 'jschon.json.JSON'>'
            # current_app.logger.info(schema_object)
            result = schema_object.evaluate(jschon.JSON(flask.request.json))
            # current_app.logger.info(result.output("basic"))

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
