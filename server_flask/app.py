import json
import os
import sys
from urllib.parse import urljoin

import requests
from flask import Flask, current_app, request
from flask_cors import CORS
from flask_json import FlaskJSON, as_json
from markupsafe import escape

from assessments import get_supported_assessments
from blueprints.patient import patient_blueprint
from database import DocumentDB
from fake import getFakePatient, getRandomFakePatients
from utils import parseInt


def create_app():
    app = Flask(__name__)

    flask_environment = os.getenv("FLASK_ENV")
    if flask_environment == "production":
        from config.prod import Config

        app.config.from_object(Config())
    elif flask_environment == "development":
        from config.dev import Config

        app.config.from_object(Config())
    else:
        raise ValueError

    # print(document_db.db_user)
    with app.app_context():
        DocumentDB.initialize()

    # Although ingress could provide CORS in production,
    # our development configuration also generates CORS requests.
    # Simple CORS wrapper of the application allows any and all requests.
    CORS(app)
    FlaskJSON(app)

    # Temporary store for patients
    patients = getRandomFakePatients()
    patient_map = {p["recordId"]: p for p in patients}

    # API TODO:
    # - check method
    # - check parameters
    # - return appropriate error message and code

    @app.route("/auth")
    @as_json
    def auth():
        return {"name": "Luke Skywalker", "authToken": "my token"}

    @app.route("/patients")
    @as_json
    def get_patients():
        return {"patients": patients}

    @app.route("/patient/<recordId>", methods=["GET"])
    @as_json
    def get_patient_data(recordId):
        if request.method == "GET":
            if recordId == None or patient_map.get(recordId, None) == None:
                return "Patient not found", 404

            return patient_map[recordId]

        else:
            return "Method not allowed", 405

    @app.route("/app/config", methods=["GET"])
    @as_json
    def get_assessments():
        if request.method == "GET":
            return {"assessments": get_supported_assessments()}

        else:
            return "Method not allowed", 405

    # Register blueprints.
    app.register_blueprint(patient_blueprint, url_prefix="/patient")

    return app


# Instead of using `flask run`, import the app normally, then run it.
# Did this because `flask run` was eating an ImportError, not giving a useful error message.
if __name__ == "__main__":
    app = create_app()

    app.run(
        host=os.getenv("FLASK_RUN_HOST"),
        port=os.getenv("FLASK_RUN_PORT"),
    )
