import copy
import datetime
import operator
import pprint

import pytz
import requests
from typing import Callable, List
from urllib.parse import urljoin

import scope.config
import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
import scope.schema
import scope.schema_utils as schema_utils
import scope.testing.fixtures_database_temp_patient
import scope.utils.compute_patient_summary


import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

QUERY = "patient/{patient_id}/summary"


def _patient_summary_assertions(summary: dict) -> None:
    # Remove "status" for schema validation
    if "status" in summary:
        del summary["status"]

    schema_utils.assert_schema(
        data=summary,
        schema=scope.schema.patient_summary_schema,
    )

    assigned_scheduled_assessments = summary["assignedScheduledAssessments"]
    for assigned_scheduled_assessment_current in assigned_scheduled_assessments:
        assert not assigned_scheduled_assessment_current["completed"]
        assert (
            date_utils.parse_date(assigned_scheduled_assessment_current["dueDate"])
            <= datetime.date.today()
        )


def test_patient_summary_get(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_safety_plan_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):

    temp_patient = database_temp_patient_factory()

    # Insert values inventory, safety plan, and scheduled assessments
    existing_values_inventory = (
        scope.database.patient.values_inventory.get_values_inventory(
            collection=temp_patient.collection
        )
    )

    fake_values_inventory = data_fake_values_inventory_factory()

    values_inventory = copy.deepcopy(existing_values_inventory)
    del values_inventory["_id"]
    values_inventory.update(fake_values_inventory)
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    existing_safety_plan = scope.database.patient.safety_plan.get_safety_plan(
        collection=temp_patient.collection
    )

    fake_safety_plan = data_fake_safety_plan_factory()

    safety_plan = copy.deepcopy(existing_safety_plan)
    del safety_plan["_id"]
    safety_plan.update(fake_safety_plan)
    scope.database.patient.safety_plan.put_safety_plan(
        collection=temp_patient.collection,
        safety_plan=safety_plan,
    )

    scheduled_assessments = data_fake_scheduled_assessments_factory()
    for scheduled_assessment_current in scheduled_assessments:
        scope.database.patient.scheduled_assessments.post_scheduled_assessment(
            collection=temp_patient.collection,
            scheduled_assessment=scheduled_assessment_current,
        )

    # Obtain a session
    session = flask_session_unauthenticated_factory()
    query = QUERY.format(patient_id=temp_patient.patient_id)
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )

    assert response.ok

    summary = response.json()
    _patient_summary_assertions(summary=summary)


def test_compute_patient_summary_values_inventory(
    data_fake_activity_factory: Callable[[], dict],
    data_fake_safety_plan_factory: Callable[[], dict],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
    data_fake_values_inventory_factory: Callable[[], dict],
):
    # Create values inventory, safety plan, and scheduled assessments
    safety_plan = data_fake_safety_plan_factory()
    scheduled_assessments = data_fake_scheduled_assessments_factory()

    # OPTION 1 - assigned is False.
    values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = False
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert not summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - assigned is True and an activity with value was created more recently.
    #          - Should be resolved.
    datetime_now = pytz.utc.localize(datetime.datetime.now())
    datetime_before = datetime_now - datetime.timedelta(minutes=30)
    values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = True
    values_inventory["assignedDateTime"] = date_utils.format_datetime(datetime_before)
    activity = data_fake_activity_factory()
    activity["editedDateTime"] = date_utils.format_datetime(datetime_now)
    activity["valueId"] = "some valueId"
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[activity],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert not summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - assigned is True and an activity was created more recently.
    #          - That activity not associated with a value.
    #          - Should still be assigned.
    datetime_now = pytz.utc.localize(datetime.datetime.now())
    datetime_before = datetime_now - datetime.timedelta(minutes=30)
    values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = True
    values_inventory["assignedDateTime"] = date_utils.format_datetime(datetime_before)
    activity = data_fake_activity_factory()
    activity["editedDateTime"] = date_utils.format_datetime(datetime_now)
    if "valueId" in activity:
        del activity["valueId"]
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[activity],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)

    # OPTION 4 - assigned is True and an activity with value was created before that.
    #          - Should be still assigned.
    datetime_now = pytz.utc.localize(datetime.datetime.now())
    datetime_before = datetime_now - datetime.timedelta(minutes=30)
    values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = True
    values_inventory["assignedDateTime"] = date_utils.format_datetime(datetime_now)
    activity = data_fake_activity_factory()
    activity["editedDateTime"] = date_utils.format_datetime(datetime_before)
    activity["valueId"] = "some valueId"
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[activity],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)


def test_compute_patient_summary_safety_plan(
    data_fake_safety_plan_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
):

    # Create values inventory, safety plan, and scheduled assessments
    values_inventory = data_fake_values_inventory_factory()
    safety_plan = data_fake_safety_plan_factory()
    scheduled_assessments = data_fake_scheduled_assessments_factory()

    # OPTION 1 - assigned is False.
    safety_plan["assigned"] = False
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - assigned is True but lastUpdatedDate = assignedDate
    safety_plan["assigned"] = True
    safety_plan["lastUpdatedDateTime"] = safety_plan["assignedDateTime"]
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - assigned is True but lastUpdatedDate > assignedDate
    safety_plan["lastUpdatedDateTime"] = date_utils.format_datetime(
        date_utils.parse_datetime(safety_plan["assignedDateTime"])
        + datetime.timedelta(days=2)
    )
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 4 - assigned is True and lastUpdatedDate < assignedDate
    safety_plan["lastUpdatedDateTime"] = date_utils.format_datetime(
        date_utils.parse_datetime(safety_plan["assignedDateTime"])
        - datetime.timedelta(days=2)
    )
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)


def test_compute_patient_summary_scheduled_assessments(
    data_fake_safety_plan_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
):
    # Create values inventory, safety plan, and scheduled assessments
    values_inventory = data_fake_values_inventory_factory()
    safety_plan = data_fake_safety_plan_factory()
    scheduled_assessments = data_fake_scheduled_assessments_factory()

    # OPTION 1 - completed is True.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = True
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - completed is False but dueDate > today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today() + datetime.timedelta(days=2)
        )
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - completed is False and dueDate = today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today()
        )
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)

    # OPTION 4 - completed is False and dueDate < today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today() - datetime.timedelta(days=1)
        )
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date.today(),
    )
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)


def test_compute_patient_summary_scheduled_assessments_multiple_due(
    data_fake_assessment_logs_factory: Callable[[], List[dict]],
):
    safety_plan = {
        "_type": "safetyPlan",
        "assigned": False,
        "assignedDateTime": "2025-08-01T00:00:00Z",
    }

    values_inventory = {
        "_type": "valuesInventory",
        "assigned": False,
        "assignedDateTime": "2025-08-01T00:00:00Z",
    }

    # Return only the most recent scheduled assessments of each assessmentId.
    scheduled_assessments = [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-05T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-07-05T00:00:00Z",
        },
    ]

    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 1),
    )

    assert sorted(
        summary["assignedScheduledAssessments"], key=operator.itemgetter("assessmentId")
    ) == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
    ]

    # Be sure that allows assessments that are due on the same day.
    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 2),
    )

    assert sorted(
        summary["assignedScheduledAssessments"], key=operator.itemgetter("assessmentId")
    ) == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
    ]

    # Return only scheduled assessments where that most recent is not already marked as completed.
    scheduled_assessments = [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-05T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-08-02T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": True,
            "dueDate": "2025-07-19T00:00:00Z",
        },
        {
            "_type": "scheduledAssessment",
            "assessmentId": "phq-9",
            "completed": False,
            "dueDate": "2025-07-05T00:00:00Z",
        },
    ]

    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=[],
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 1),
    )

    assert sorted(
        summary["assignedScheduledAssessments"], key=operator.itemgetter("assessmentId")
    ) == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
    ]

    # We have had low confidence in the code which marks completed.
    # For robustness, explicitly check the lack of a patient-submitted assessmentLog since one was due.

    # In this case, logs are prior to the most recent due date.
    assessment_logs = [
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-01T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-07T18:30:00Z",
        },
    ]

    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=assessment_logs,
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 1),
    )

    assert sorted(
        summary["assignedScheduledAssessments"], key=operator.itemgetter("assessmentId")
    ) == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
    ]

    # In this case, a log come after the most recent due date, but was not patient submitted or was the wrong assessment.
    assessment_logs = [
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-01T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-07T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": False,
            "recordedDateTime": "2025-07-25T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "phq-9",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-25T18:30:00Z",
        },
    ]

    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=assessment_logs,
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 1),
    )

    assert sorted(
        summary["assignedScheduledAssessments"], key=operator.itemgetter("assessmentId")
    ) == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "gad-7",
            "completed": False,
            "dueDate": "2025-07-19T00:00:00Z",
        },
    ]

    # In this case, a log come after the most recent due date and was patient submitted.
    assessment_logs = [
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-01T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-07T18:30:00Z",
        },
        {
            "_type": "assessmentLog",
            "assessmentId": "gad-7",
            "patientSubmitted": True,
            "recordedDateTime": "2025-07-25T18:30:00Z",
        },
    ]

    summary = scope.utils.compute_patient_summary.compute_patient_summary(
        activity_documents=[],
        assessment_log_documents=assessment_logs,
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
        date_due=datetime.date(2025, 8, 1),
    )

    assert (
        sorted(
            summary["assignedScheduledAssessments"],
            key=operator.itemgetter("assessmentId"),
        )
        == []
    )
