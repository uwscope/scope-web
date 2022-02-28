from dataclasses import dataclass
import datetime
import jschon
import requests
from typing import Callable, List
from urllib.parse import urljoin

import scope.config
import scope.database.date_utils as date_utils
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
from scope.schema import patient_summary_schema

import scope.testing.fixtures_database_temp_patient

import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

QUERY = "patient/{patient_id}/summary"


def _patient_summary_assertions(summary: dict) -> None:
    # Remove "status" for schema validation
    assert "status" in summary
    del summary["status"]

    schema_result = patient_summary_schema.evaluate(jschon.JSON(summary))
    assert schema_result.valid

    assigned_scheduled_assessments = summary["assignedScheduledAssessments"]
    for assigned_scheduled_assessment_current in assigned_scheduled_assessments:
        assert assigned_scheduled_assessment_current["completed"] == False
        assert (
            date_utils.format_string(assigned_scheduled_assessment_current["dueDate"])
            <= datetime.datetime.today()
        )


def test_patient_summary(
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
    values_inventory = data_fake_values_inventory_factory()
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )
    safety_plan = data_fake_safety_plan_factory()
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


def test_patient_summary_values_inventory(
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
    values_inventory = data_fake_values_inventory_factory()

    # Option 1 - values inventory, assigned is False.
    values_inventory["assigned"] = False
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    safety_plan = data_fake_safety_plan_factory()
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
    assert summary["assignedValuesInventory"] == False
    _patient_summary_assertions(summary=summary)

    # Option 2 - values inventory, assigned is True and acivity exists in values
    values_inventory = data_fake_values_inventory_factory()
    while not len(values_inventory.get("values", [])) > 0:
        values_inventory = data_fake_values_inventory_factory()

    values_inventory["_rev"] = 1
    values_inventory["assigned"] = True
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok
    summary = response.json()
    assert summary["assignedValuesInventory"] == False
    _patient_summary_assertions(summary=summary)

    # Option 3 - values inventory, assigned is True and no acivity exists in values
    values_inventory = data_fake_values_inventory_factory()
    while not len(values_inventory.get("values", [])) == 0:
        values_inventory = data_fake_values_inventory_factory()

    values_inventory["_rev"] = 2
    values_inventory["assigned"] = True
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok
    summary = response.json()
    assert summary["assignedValuesInventory"] == True
    _patient_summary_assertions(summary=summary)


def test_patient_summary_safety_plan(
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
    values_inventory = data_fake_values_inventory_factory()
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    safety_plan = data_fake_safety_plan_factory()
    # Option 1 - safety plan, assigned is False.
    safety_plan["assigned"] = False
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
    assert summary["assignedSafetyPlan"] == False
    _patient_summary_assertions(summary=summary)

    # Option 2 - safety plan, assigned is True but lastUpdatedDate = assignedDate
    safety_plan["_rev"] = 1
    safety_plan["assigned"] = True
    safety_plan["lastUpdatedDate"] = safety_plan["assignedDate"]
    scope.database.patient.safety_plan.put_safety_plan(
        collection=temp_patient.collection,
        safety_plan=safety_plan,
    )

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok
    summary = response.json()
    assert summary["assignedSafetyPlan"] == False
    _patient_summary_assertions(summary=summary)

    # Option 3 - safety plan, assigned is True but lastUpdatedDate > assignedDate
    safety_plan["_rev"] = 2
    safety_plan["assigned"] = True
    safety_plan["lastUpdatedDate"] = date_utils.format_date(
        date_utils.format_string(safety_plan["assignedDate"])
        + datetime.timedelta(days=2)
    )
    scope.database.patient.safety_plan.put_safety_plan(
        collection=temp_patient.collection,
        safety_plan=safety_plan,
    )

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok
    summary = response.json()
    assert summary["assignedSafetyPlan"] == False
    _patient_summary_assertions(summary=summary)

    # Option 4 - safety plan, assigned is True and lastUpdatedDate < assignedDate
    safety_plan["_rev"] = 3
    safety_plan["assigned"] = True
    safety_plan["lastUpdatedDate"] = date_utils.format_date(
        date_utils.format_string(safety_plan["assignedDate"])
        - datetime.timedelta(days=2)
    )
    scope.database.patient.safety_plan.put_safety_plan(
        collection=temp_patient.collection,
        safety_plan=safety_plan,
    )

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok
    summary = response.json()
    assert summary["assignedSafetyPlan"] == True
    _patient_summary_assertions(summary=summary)


def test_patient_summary_scheduled_assessments(
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
    values_inventory = data_fake_values_inventory_factory()
    scope.database.patient.values_inventory.put_values_inventory(
        collection=temp_patient.collection,
        values_inventory=values_inventory,
    )

    safety_plan = data_fake_safety_plan_factory()
    scope.database.patient.safety_plan.put_safety_plan(
        collection=temp_patient.collection,
        safety_plan=safety_plan,
    )

    scheduled_assessments = data_fake_scheduled_assessments_factory()
    # Option 1 - scheduled assessments, completed is True.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = True
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
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # Option 2 - scheduled assessments, completed is False but dueDate > today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.datetime.today() + datetime.timedelta(days=2)
        )

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
    assert summary["assignedScheduledAssessments"] == []
    _patient_summary_assertions(summary=summary)

    # Option 3 - scheduled assessments, completed is False and dueDate = today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.datetime.today()
        )

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
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)

    # Option 4 - scheduled assessments, completed is False and dueDate < today.
    for scheduled_assessment_current in scheduled_assessments:
        scheduled_assessment_current["completed"] = False
        scheduled_assessment_current["dueDate"] = date_utils.format_date(
            datetime.datetime.today() - datetime.timedelta(days=1)
        )

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
    assert summary["assignedScheduledAssessments"] != []
    _patient_summary_assertions(summary=summary)
