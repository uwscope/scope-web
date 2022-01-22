from flask import Flask, request
from flask_json import as_json


def create_registry():
    registry = Flask(__name__)

    @registry.route("/patients", methods=["GET", "POST"])
    @as_json
    def get_patients():
        # NOTE: In-progress. More subschemas need to be added.
        if request.method == "GET":
            print("Gets the list of all patients and returns an array of patients")

        # NOTE: In-progress. More subschemas need to be added.
        elif request.method == "POST":
            print("Creates a new patient record and returns the patient")

        else:
            return "Method not allowed", 405

    @registry.route("/patients/<recordId>", methods=["GET"])
    @as_json
    def get_patient_data(recordId):
        # NOTE: Done. Takes patient_collection_name instead of `recordId`. URL is /patients/<patient_collection_name>
        if request.method == "GET":
            print("Gets the full patient data by id and returns the patient")
        # NOTE: Done.
        elif request.method == "PUT":
            return "Method not allowed", 405
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/values", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_values(recordId):  # Uses values-inventory.json subschema
        # NOTE: Done.
        if request.method == "GET":
            print(
                "Gets the patient values inventory data by patient id and returns the patient values inventory data"
            )
        # NOTE: Done.
        elif request.method == "PUT":
            print(
                "Updates the patient values inventory data by patient id and returns the patient values inventory data"
            )
        # NOTE: Done.
        else:
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
        "/patients/<recordId>/clinicalhistory", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_values(recordId):  # Uses clinical-history.json subschema
        # NOTE: Done.
        if request.method == "GET":
            print(
                "Gets the patient clinical history data by patient id and returns the patient clinical history data"
            )

        # NOTE: Done
        elif request.method == "PUT":
            print(
                "Updates the patient clinical history data by patient id and returns the patient clinical history data"
            )

        # NOTE: Done
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/profile", methods=["GET", "PUT"]
    )  # GET for subschemas is not needed for current client function but putting it there for completeness
    @as_json
    def get_patient_profile(recordId):  # Uses patient-profile.json subschema
        # NOTE: DONE.
        if request.method == "GET":
            print(
                "Gets the patient profile data by id and returns the patient profile data"
            )
        # NOTE: Done.
        elif request.method == "PUT":
            print(
                "Updates the patient profile data by id and returns the patient profile data"
            )
        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route("/patients/<recordId>/sessions", methods=["GET", "POST"])
    @as_json
    def get_patient_sessions(recordId):
        # NOTE: Done.
        if request.method == "GET":
            print("Gets the list of all sessions and returns an array of sessions")

        # NOTE: Done.
        elif request.method == "POST":
            print("Creates a new session in the patient record and returns the session")

        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route("/patients/<recordId>/sessions/<sessionId>", methods=["GET", "PUT"])
    @as_json
    def get_patient_session(recordId, sessionId):
        # NOTE: Done.
        if request.method == "GET":
            print("Gets the full session data by id and returns the session")

        # NOTE: Done. Question - do we need to send sessionId here?
        elif request.method == "PUT":
            print("Updates the session data by id and returns the session")
        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route("/patients/<recordId>/casereviews", methods=["GET", "POST"])
    @as_json
    def get_patient_casereviews(recordId):
        # NOTE: Done.
        if request.method == "GET":
            print(
                "Gets the list of all case reviews and returns an array of case reviews"
            )
        # NOTE: Done.
        elif request.method == "POST":
            print(
                "Creates a new case review in the patient record and returns the case review"
            )
        # NOTE: Done.
        else:
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/casereviews/<reviewId>", methods=["GET", "PUT"]
    )
    @as_json
    def get_patient_casereview(recordId, reviewId):
        # NOTE: Done.
        if request.method == "GET":
            print("Gets the full case review data by id and returns the case review")
        # NOTE: Done.
        elif request.method == "PUT":
            print("Updates the case review data by id and returns the case review")
        # NOTE: Done.
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

    @registry.route("/patients/<recordId>/assessmentlogs", methods=["GET", "POST"])
    @as_json
    def get_patient_assessmentlogs(recordId):
        # NOTE: In-progress. Conversation pending with Jina.
        if request.method == "GET":
            print(
                "Gets the list of assessment logs for patient and returns an array of assessment logs"
            )
        # NOTE: In-progress. Conversation pending with Jina.
        elif request.method == "POST":
            print(
                "Creates a new assessment log in the patient record and returns the assessment log"
            )

        else:
            return "Method not allowed", 405

    @registry.route(
        "/patients/<recordId>/assessmentlogs/<logId>", methods=["GET", "PUT"]
    )
    @as_json
    def get_patient_assessmentlog(recordId, logId):
        # NOTE: In-progress. Conversation pending with Jina.
        if request.method == "GET":
            print(
                "Gets the assessment log by id for patient and returns the assessment log"
            )
        # NOTE: In-progress. Conversation pending with Jina.
        elif request.method == "PUT":
            print("Updates the assessment log by id and returns the assessment log")
        # NOTE: In-progress. Conversation pending with Jina.
        else:
            return "Method not allowed", 405

    return registry
