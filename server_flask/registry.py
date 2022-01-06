from flask import Flask, request
from flask_json import as_json


def create_registry():
    registry = Flask(__name__)

    @registry.route("/patients", methods=["GET", "POST"])
    @as_json
    def get_patients():

        if request.method == "GET":
            # NOTE: Done.
            print("Gets the list of all patients and returns an array of patients")

        elif request.method == "POST":
            # NOTE: In-progress. More subschemas need to be added.
            print("Creates a new patient record and returns the patient")

        else:
            # NOTE: In-progress. More subschemas need to be added.
            return "Method not allowed", 405

    @registry.route("/patients/<recordId>", methods=["GET"])
    @as_json
    def get_patient_data(recordId):
        if request.method == "GET":
            # NOTE: Done. Takes patient_collection_name instead of `recordId`. URL is /patients/<patient_collection_name>
            print("Gets the full patient data by id and returns the patient")

        elif request.method == "PUT":
            # NOTE: Done.
            return "Method not allowed", 405
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/values", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_values(recordId):  # Uses values-inventory.json subschema
        if request.method == "GET":
            # NOTE: Done.
            print(
                "Gets the patient values inventory data by patient id and returns the patient values inventory data"
            )

        elif request.method == "PUT":
            # NOTE: Done.
            print(
                "Updates the patient values inventory data by patient id and returns the patient values inventory data"
            )
        else:
            # NOTE: Done.
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/safety", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_values(recordId):  # Uses safety-plan.json subschema
        # NOTE: Done.
        if request.method == "GET":
            print(
                "Gets the patient safety plan data by patient id and returns the patient safety plan data"
            )
        # NOTE: Done.
        elif request.method == "PUT":
            print(
                "Updates the patient safety plan data by patient id and returns the patient safety plan data"
            )
        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patient/<recordId>/clinicalhistory", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_values(recordId):  # Uses clinical-history.json subschema
        # NOTE: Done.
        if request.method == "GET":
            print(
                "Gets the patient clinical history data by patient id and returns the patient clinical history data"
            )

        # NOTE: Done.
        elif request.method == "PUT":
            print(
                "Updates the patient clinical history data by patient id and returns the patient clinical history data"
            )

        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patient/<recordId>/profile", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_profile(recordId):  # Uses patient-profile.json subschema
        if request.method == "GET":
            print(
                "Gets the patient profile data by id and returns the patient profile data"
            )

        elif request.method == "PUT":
            print(
                "Updates the patient profile data by id and returns the patient profile data"
            )

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/sessions", methods=["GET", "POST"])
    @as_json
    def get_patient_sessions(recordId):
        if request.method == "GET":
            print("Gets the list of all sessions and returns an array of sessions")

        elif request.method == "POST":
            print("Creates a new session in the patient record and returns the session")

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/session/<sessionId>", methods=["GET", "PUT"])
    @as_json
    def get_patient_session(recordId, sessionId):
        if request.method == "GET":
            print("Gets the full session data by id and returns the session")

        elif request.method == "PUT":
            print("Updates the session data by id and returns the session")

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/casereviews", methods=["GET", "POST"])
    @as_json
    def get_patient_casereviews(recordId):
        if request.method == "GET":
            print(
                "Gets the list of all case reviews and returns an array of case reviews"
            )

        elif request.method == "POST":
            print(
                "Creates a new case review in the patient record and returns the case review"
            )

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/casereview/<reviewId>", methods=["GET", "PUT"])
    @as_json
    def get_patient_casereview(recordId, reviewId):
        if request.method == "GET":
            print("Gets the full case review data by id and returns the case review")

        elif request.method == "PUT":
            print("Updates the case review data by id and returns the case review")

        else:
            return "Method not allowed", 405

    @registry.route(
        "/patient/<recordId>/assessment/<assessmentId>", methods=["GET", "PUT"]
    )
    @as_json
    def get_patient_assessments(recordId, assessmentId):
        if request.method == "GET":
            print("Gets the full assessment metadata by id and returns the assessment")

        elif request.method == "PUT":
            print("Updates the assessment metadata by id and returns the assessment")

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/assessmentlogs", methods=["GET", "POST"])
    @as_json
    def get_patient_assessmentlogs(recordId):
        if request.method == "GET":
            print(
                "Gets the list of assessment logs for patient and returns an array of assessment logs"
            )

        elif request.method == "POST":
            print(
                "Creates a new assessment log in the patient record and returns the assessment log"
            )

        else:
            return "Method not allowed", 405

    @registry.route("/patient/<recordId>/assessmentlog/<logId>", methods=["GET", "PUT"])
    @as_json
    def get_patient_assessmentlog(recordId, logId):
        if request.method == "GET":
            print(
                "Gets the assessment log by id for patient and returns the assessment log"
            )

        elif request.method == "PUT":
            print("Updates the assessment log by id and returns the assessment log")

        else:
            return "Method not allowed", 405

    return registry
