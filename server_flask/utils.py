import json
from functools import wraps

from flask import abort, current_app, jsonify, request
from flask_json import json_response
from jschon import JSON


def parseInt(text):
    return int(text) if text.isdecimal() else None


# TODO: Confirm location of the function with James.


def validate_schema(schema_object):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # For .evaluate to work, its argument needs to be of type '<class 'jschon.json.JSON'>'
            current_app.logger.info(schema_object)
            result = schema_object.evaluate(JSON.loads(json.dumps(request.json)))
            current_app.logger.info(result.output("basic"))

            if result.output("flag")["valid"] == False:
                abort(
                    400,
                    jsonify(
                        message="Invalid contents.",
                        error=result.output("basic"),
                    ),
                )
            return f(*args, **kwargs)

        return wrapper

    return decorator
