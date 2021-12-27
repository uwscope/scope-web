import json
from functools import wraps

from flask import abort, jsonify, request
from flask_json import json_response


def parseInt(text):
    return int(text) if text.isdecimal() else None


# TODO: Confirm location of the function with James.
def validate_schema(schema_object):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # For .evaluate to work, its argument needs to be of type '<class 'jschon.json.JSON'>'
            result = schema_object.evaluate(
                json_response.loads(json.dumps(request.json))
            )
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
