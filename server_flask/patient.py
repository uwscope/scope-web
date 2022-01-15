from flask import Flask, request
from flask_json import as_json


def create_patient_service():
    patient_service = Flask(__name__)

    @patient_service.route("/patient/values", methods=["GET", "PUT"])
    @as_json
    def get_patient_values():
        # NOTE: Done
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the values inventory and returns an array of life area values data"
            )
        # NOTE: Done
        elif request.method == "PUT":
            print(
                "For the authenticated patient, updates the values inventory and returns an array of life area values data"
            )

        # Should we pull CRUD APIs for values inventory?
        # NOTE: Done
        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/safety", methods=["GET", "PUT"])
    @as_json
    def get_patient_safety_plan():
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the safety plan and returns the safety plan data"
            )

        elif request.method == "PUT":
            print(
                "For the authenticated patient, updates the safety plan and returns the safety plan data"
            )

        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/activities/schedule", methods=["GET"])
    @as_json
    def get_patient_schedule():
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the list of all scheduled activities, past and future"
            )
        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/assessments/schedule", methods=["GET"])
    @as_json
    def get_patient_schedule():
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the list of all scheduled assessments, past and future"
            )
        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/activities", methods=["GET", "POST"])
    @as_json
    def get_patient_activities():

        if request.method == "GET":
            print(
                "For the authenticated patient, gets the list of all activities, enabled or not, and returns an array of activity data"
            )

        elif request.method == "POST":
            print(
                "For the authenticated patient, creates a new activity, and returns the created activity data"
            )

        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/activity/<activityId>", methods=["GET", "PUT"])
    @as_json
    def get_patient_activity(activityId):
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the full activity data by id and returns the activity data"
            )

        elif request.method == "PUT":
            print(
                "For the authenticated patient, updates the activity data by id and returns the updated activity"
            )

        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/config", methods=["GET"])
    @as_json
    def get_patient_config():
        if request.method == "GET":
            print(
                "For the authenticated patient, gets the app configurations like flags or assignments and returns the patient app configuration"
            )

        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/activitylogs", methods=["GET", "POST"])
    @as_json
    def get_patient_activitylogs():
        if request.method == "GET":
            print(
                "Gets the list of activity logs for patient and returns an array of activity logs"
            )

        elif request.method == "POST":
            print(
                "Creates a new activity log in the patient record and returns the activity log"
            )  # could return the full list

        else:
            return "Method not allowed", 405

    @patient_service.route("/patient/assessmentlogs", methods=["GET", "POST"])
    @as_json
    def get_patient_assessmentlogs():
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

    @patient_service.route("/patient/moodlogs", methods=["GET", "POST"])
    @as_json
    def get_patient_moodlogs():
        if request.method == "GET":
            print(
                "Gets the list of mood logs for patient and returns an array of mood logs"
            )

        elif request.method == "POST":
            print(
                "Creates a new mood log in the patient record and returns the mood log"
            )

        else:
            return "Method not allowed", 405

    return patient_service
