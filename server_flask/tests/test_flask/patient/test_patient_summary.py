import copy
import datetime
import requests
from typing import Callable, List
from urllib.parse import urljoin

import blueprints.patient.summary
import scope.config
import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
import scope.schema
import scope.schema_utils as schema_utils
import scope.testing.fixtures_database_temp_patient


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
            date_utils.parse_date(
                assigned_scheduled_assessment_current["dueDate"]
            ).date()
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
    data_fake_safety_plan_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
):
    # Create values inventory, safety plan, and scheduled assessments
    safety_plan = data_fake_safety_plan_factory()
    scheduled_assessments = data_fake_scheduled_assessments_factory()

    # OPTION 1 - assigned is False.
    values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = False
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert not summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - assigned is True and activity exists in values
    values_inventory = data_fake_values_inventory_factory()
    while not len(values_inventory.get("values", [])) > 0:
        values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = True
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert not summary["assignedValuesInventory"]
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - assigned is True and no acivity exists in values
    values_inventory = data_fake_values_inventory_factory()
    while not len(values_inventory.get("values", [])) == 0:
        values_inventory = data_fake_values_inventory_factory()
    values_inventory["assigned"] = True
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
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
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - assigned is True but lastUpdatedDate = assignedDate
    safety_plan["assigned"] = True
    safety_plan["lastUpdatedDateTime"] = safety_plan["assignedDateTime"]
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - assigned is True but lastUpdatedDate > assignedDate
    safety_plan["lastUpdatedDateTime"] = date_utils.format_datetime(
        date_utils.parse_datetime(safety_plan["assignedDateTime"])
        + datetime.timedelta(days=2)
    )
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert not summary["assignedSafetyPlan"]
    _patient_summary_assertions(summary=summary)

    # OPTION 4 - assigned is True and lastUpdatedDate < assignedDate
    safety_plan["lastUpdatedDateTime"] = date_utils.format_datetime(
        date_utils.parse_datetime(safety_plan["assignedDateTime"])
        - datetime.timedelta(days=2)
    )
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
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
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # OPTION 2 - completed is False but dueDate > today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today() + datetime.timedelta(days=2)
        )
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # OPTION 3 - completed is False and dueDate = today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today()
        )
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)

    # OPTION 4 - completed is False and dueDate < today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.date.today() - datetime.timedelta(days=1)
        )
    summary = blueprints.patient.summary.compute_patient_summary(
        safety_plan_document=safety_plan,
        scheduled_assessment_documents=scheduled_assessments,
        values_inventory_document=values_inventory,
    )
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)
