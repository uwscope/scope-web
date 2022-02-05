from pprint import pprint
from typing import Callable
from urllib.parse import urljoin

import pymongo.database
import pytest
import requests
import scope.config
import scope.database.patients
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


def test_get_patients(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving patients.
    """

    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients",
        ),
    )
    assert response.ok

    pprint(response.json())

    assert False


# TODO: James to Review
@pytest.mark.skip(reason="Not reviewed")
def test_flask_get_all_patients(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a list of patients.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all patients
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/",
        ),
    )
    assert response.ok

    # "patients" is a list
    response_patients = response.json()["patients"]

    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["assessments"] = sorted(
        data_fake_patient["assessments"], key=lambda i: i["_id"]
    )
    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["scheduledAssessments"] = sorted(
        data_fake_patient["scheduledAssessments"], key=lambda i: i["_id"]
    )
    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["assessmentLogs"] = sorted(
        data_fake_patient["assessmentLogs"], key=lambda i: i["_id"]
    )

    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["activities"] = sorted(
        data_fake_patient["activities"], key=lambda i: i["_id"]
    )
    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["scheduledActivities"] = sorted(
        data_fake_patient["scheduledActivities"], key=lambda i: i["_id"]
    )
    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["activityLogs"] = sorted(
        data_fake_patient["activityLogs"], key=lambda i: i["_id"]
    )

    # For assert to work on two list of dicts, the order needs to be same.
    data_fake_patient["moodLogs"] = sorted(
        data_fake_patient["moodLogs"], key=lambda i: i["_id"]
    )

    for rp in response_patients:
        rp["assessments"] = sorted(rp["assessments"], key=lambda i: i["_id"])
        rp["scheduledAssessments"] = sorted(
            rp["scheduledAssessments"], key=lambda i: i["_id"]
        )
        rp["assessmentLogs"] = sorted(rp["assessmentLogs"], key=lambda i: i["_id"])

        rp["activities"] = sorted(rp["activities"], key=lambda i: i["_id"])
        rp["activityLogs"] = sorted(rp["activityLogs"], key=lambda i: i["_id"])
        rp["scheduledActivities"] = sorted(
            rp["scheduledActivities"], key=lambda i: i["_id"]
        )

        rp["moodLogs"] = sorted(rp["moodLogs"], key=lambda i: i["_id"])

    # Ensure list includes our fake patient
    assert data_fake_patient in response_patients

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# TODO: James to Review
@pytest.mark.skip(reason="Not reviewed")
def test_flask_get_patient(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a patient via patient collection name.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient by sending its collection name
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format(patient_collection_name),
        ),
    )
    assert response.ok
    response_json = response.json()
  
    # Ensure body of response is our fake patient
    assert response_json.get("_type") == data_fake_patient.get("_type")
    assert response_json.get("identity") == data_fake_patient.get("identity")
    assert response_json.get("patientProfile") == data_fake_patient.get(
        "patientProfile"
    )
    assert response_json.get("clinicalHistory") == data_fake_patient.get(
        "clinicalHistory"
    )
    assert response_json.get("valuesInventory") == data_fake_patient.get(
        "valuesInventory"
    )
    assert response_json.get("safetyPlan") == data_fake_patient.get("safetyPlan")
    assert response_json.get("sessions") == data_fake_patient.get("sessions")
    assert response_json.get("caseReviews") == data_fake_patient.get("caseReviews")

    # NOTE: assert response_json["assessmentLogs"] == data_fake_patient["assessmentLogs"] fails because the order of dicts in the two lists is different.
    assert sorted(response_json["assessments"], key=lambda i: i["_id"]) == sorted(
        data_fake_patient["assessments"], key=lambda i: i["_id"]
    )
    assert sorted(
        response_json["scheduledAssessments"], key=lambda i: i["_id"]
    ) == sorted(data_fake_patient["scheduledAssessments"], key=lambda i: i["_id"])
    assert sorted(response_json["assessmentLogs"], key=lambda i: i["_id"]) == sorted(
        data_fake_patient["assessmentLogs"], key=lambda i: i["_id"]
    )
    assert sorted(response_json["activities"], key=lambda i: i["_id"]) == sorted(
        data_fake_patient["activities"], key=lambda i: i["_id"]
    )
    assert sorted(
        response_json["scheduledActivities"], key=lambda i: i["_id"]
    ) == sorted(data_fake_patient["scheduledActivities"], key=lambda i: i["_id"])
    assert sorted(response_json["activityLogs"], key=lambda i: i["_id"]) == sorted(
        data_fake_patient["activityLogs"], key=lambda i: i["_id"]
    )

    assert sorted(response_json["moodLogs"], key=lambda i: i["_id"]) == sorted(
        data_fake_patient["moodLogs"], key=lambda i: i["_id"]
    )

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# TODO: James to Review
@pytest.mark.skip(reason="Not reviewed")
def test_flask_get_nonexistent_patient(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that we get a 404 if we try to get a non-existant patient.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Attempt to retrieve the patient using the _id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format("patient_nonexistant"),
        ),
    )
    assert response.status_code == 404  # Not Found


# TODO: James to Review
@pytest.mark.skip(reason="Not reviewed")
def test_flask_create_patient(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can create a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient using the _id
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/",
        ),
        json=data_fake_patient,
    )

    assert response.status_code == 200
    response_json = response.json()

    # Convert `bson.objectid.ObjectId` to `str`
    for v in response_json.values():
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["sessions"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["caseReviews"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["assessments"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["scheduledAssessments"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["assessmentLogs"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["activities"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["scheduledActivities"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["activityLogs"]:
        if isinstance(v, dict):
            v.pop("_id", None)
    for v in response_json["moodLogs"]:
        if isinstance(v, dict):
            v.pop("_id", None)

    # Ensure body of response is our fake patient
    assert response_json["_type"] == data_fake_patient["_type"]
    assert response_json["identity"] == data_fake_patient["identity"]
    assert response_json["patientProfile"] == data_fake_patient["patientProfile"]
    assert response_json["clinicalHistory"] == data_fake_patient["clinicalHistory"]
    assert response_json["valuesInventory"] == data_fake_patient["valuesInventory"]
    assert response_json["safetyPlan"] == data_fake_patient["safetyPlan"]
    assert response_json["sessions"] == data_fake_patient["sessions"]
    assert response_json["caseReviews"] == data_fake_patient["caseReviews"]
    assert response_json["assessments"] == data_fake_patient["assessments"]

    # NOTE: assert response_json["assessmentLogs"] == data_fake_patient["assessmentLogs"] fails because the order of dicts in the two lists is different.
    assert sorted(
        response_json["assessments"],
        key=lambda i: (i["_assessment_id"]),
    ) == sorted(
        data_fake_patient["assessments"],
        key=lambda i: (i["_assessment_id"]),
    )
    assert sorted(
        response_json["scheduledAssessments"],
        key=lambda i: (i["_schedule_id"]),
    ) == sorted(
        data_fake_patient["scheduledAssessments"],
        key=lambda i: (i["_schedule_id"]),
    )
    assert sorted(
        response_json["assessmentLogs"],
        key=lambda i: (i["_log_id"]),
    ) == sorted(
        data_fake_patient["assessmentLogs"],
        key=lambda i: (i["_log_id"]),
    )

    assert sorted(
        response_json["activities"],
        key=lambda i: (i["_activity_id"]),
    ) == sorted(
        data_fake_patient["activities"],
        key=lambda i: (i["_activity_id"]),
    )
    assert sorted(
        response_json["scheduledActivities"],
        key=lambda i: (i["_schedule_id"]),
    ) == sorted(
        data_fake_patient["scheduledActivities"],
        key=lambda i: (i["_schedule_id"]),
    )
    assert sorted(
        response_json["activityLogs"],
        key=lambda i: (i["_log_id"]),
    ) == sorted(
        data_fake_patient["activityLogs"],
        key=lambda i: (i["_log_id"]),
    )

    assert sorted(response_json["moodLogs"], key=lambda i: (i["_log_id"]),) == sorted(
        data_fake_patient["moodLogs"],
        key=lambda i: (i["_log_id"]),
    )

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# TODO: James to Review
@pytest.mark.skip(reason="Not reviewed")
def test_flask_update_patient_405(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we get a 405 if we try to PUT patient.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Update the same patient by sending its collection name
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format("patient_nonexistant"),
        ),
        json={},
    )
    assert response.status_code == 405
