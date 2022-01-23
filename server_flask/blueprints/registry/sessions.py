import http
from functools import wraps

import scope.database
import scope.database.patient.sessions
from flask import Blueprint, abort, current_app, jsonify, request
from flask_json import as_json
from request_context import request_context
from scope.schema import session_schema
from utils import validate_schema

registry_sessions_blueprint = Blueprint(
    "registry_sessions_blueprint", __name__, url_prefix="/patients"
)


@registry_sessions_blueprint.route(
    "/<string:patient_collection>/sessions", methods=["GET"]
)
@as_json
def get_sessions(patient_collection):
    context = request_context()

    result = scope.database.patient.sessions.get_sessions(
        database=context.database, collection_name=patient_collection
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_sessions_blueprint.route(
    "/<string:patient_collection>/sessions", methods=["POST"]
)
@validate_schema(session_schema)
@as_json
def create_session(patient_collection):
    """
    Adds a new session in the patient record and returns the session
    """

    session = request.json

    if "_id" in session:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    context = request_context()

    result = scope.database.patient.sessions.create_session(
        database=context.database,
        collection_name=patient_collection,
        session=session,
    )

    if result is not None:
        session.update({"_id": str(result.inserted_id)})
        return session, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422


@registry_sessions_blueprint.route(
    "/<string:patient_collection>/sessions/<string:session_id>", methods=["GET"]
)
@as_json
def get_session(patient_collection, session_id):
    context = request_context()

    result = scope.database.patient.sessions.get_session(
        database=context.database,
        collection_name=patient_collection,
        session_id=session_id,
    )

    if result:
        return result, http.HTTPStatus.OK
    else:
        abort(http.HTTPStatus.NOT_FOUND)


@registry_sessions_blueprint.route(
    "/<string:patient_collection>/sessions/<string:session_id>", methods=["PUT"]
)
@validate_schema(session_schema)
@as_json
def update_session(patient_collection, session_id):

    session = request.json

    if "_id" in session:
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

    # Update _rev
    session["_rev"] = session["_rev"] + 1

    # NOTE: Assume client is not sending session_id as part of json.
    session.update({"_session_id": session_id})

    context = request_context()

    result = scope.database.patient.sessions.update_session(
        database=context.database,
        collection_name=patient_collection,
        session=session,
    )

    if result is not None:
        session.update({"_id": str(result.inserted_id)})
        return session, http.HTTPStatus.OK
    else:
        # NOTE: Send back the latest version of the document. Hold off on that.
        abort(http.HTTPStatus.UNPROCESSABLE_ENTITY)  # 422
