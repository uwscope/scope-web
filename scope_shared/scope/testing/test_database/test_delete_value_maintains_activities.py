"""
A delete to scope.database.patient.values must "other" the associated activities.
"""

import datetime
import pprint
import pytz
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.values
import scope.database.patient.activities
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient


def test_delete_value(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_value_factory: Callable[[], dict],
    data_fake_activities_factory: Callable[[], List[dict]],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake value
    fake_value = data_fake_value_factory()
    fake_value_post_result = scope.database.patient.values.post_value(
        collection=patient_collection, value=fake_value
    )
    assert fake_value_post_result.inserted_count == 1
    inserted_fake_value = fake_value_post_result.document

    # Obtain fake activities, update their "valueId", and insert them into db.
    fake_activities = data_fake_activities_factory()
    for _fake_activity in fake_activities:
        _fake_activity.update({"valueId": inserted_fake_value["valueId"]})
        _fake_activity_post_result = scope.database.patient.activities.post_activity(
            collection=patient_collection, activity=_fake_activity
        )
        assert _fake_activity_post_result.inserted_count == 1

    # Get activities matching "valueId"
    activities_matching_value_id = [
        activity_current
        for activity_current in scope.database.patient.activities.get_activities(
            collection=patient_collection
        )
        if activity_current.get("valueId") == inserted_fake_value["valueId"]
    ]
    assert len(activities_matching_value_id) == len(fake_activities)

    # Delete value
    delete_value_put_result = scope.database.patient.values.delete_value(
        collection=patient_collection,
        set_id=inserted_fake_value[scope.database.patient.values.SEMANTIC_SET_ID],
        rev=inserted_fake_value["_rev"],
    )
    assert delete_value_put_result.inserted_count == 1

    # Get "othered" activities
    other_activities = scope.database.patient.activities.get_activities(
        collection=patient_collection
    )

    for other_activity, activity_matching_value_id in zip(
        other_activities, activities_matching_value_id
    ):
        assert other_activity["_rev"] == activity_matching_value_id["_rev"] + 1
        assert "valueId" not in other_activity

        del other_activity["_id"]
        del activity_matching_value_id["_id"]
        del other_activity["_rev"]
        del activity_matching_value_id["_rev"]
        del activity_matching_value_id["valueId"]

    assert other_activities == activities_matching_value_id


def test_delete_value_stress_testing(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_value_factory: Callable[[], dict],
    data_fake_activities_factory: Callable[[], List[dict]],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake value
    fake_value = data_fake_value_factory()
    fake_value_post_result = scope.database.patient.values.post_value(
        collection=patient_collection, value=fake_value
    )
    assert fake_value_post_result.inserted_count == 1
    inserted_fake_value = fake_value_post_result.document

    # Obtain fake activities, update their "valueId", and insert them into db.
    fake_activities_with_value_id = data_fake_activities_factory()
    for _fake_activity in fake_activities_with_value_id:
        _fake_activity.update({"valueId": inserted_fake_value["valueId"]})
        _fake_activity_post_result = scope.database.patient.activities.post_activity(
            collection=patient_collection, activity=_fake_activity
        )
        assert _fake_activity_post_result.inserted_count == 1

    # Obtain more fake activities and insert them into db.
    fake_activities = data_fake_activities_factory()
    for _fake_activity in fake_activities:
        _fake_activity_post_result = scope.database.patient.activities.post_activity(
            collection=patient_collection, activity=_fake_activity
        )
        assert _fake_activity_post_result.inserted_count == 1

    # Get activities matching "valueId"
    activities_matching_value_id = [
        activity_current
        for activity_current in scope.database.patient.activities.get_activities(
            collection=patient_collection
        )
        if activity_current.get("valueId") == inserted_fake_value["valueId"]
    ]
    assert len(activities_matching_value_id) == len(fake_activities_with_value_id)

    # Delete value
    delete_value_put_result = scope.database.patient.values.delete_value(
        collection=patient_collection,
        set_id=inserted_fake_value[scope.database.patient.values.SEMANTIC_SET_ID],
        rev=inserted_fake_value["_rev"],
    )
    assert delete_value_put_result.inserted_count == 1

    # Get "othered" activities
    other_activities = [
        activity_current
        for activity_current in scope.database.patient.activities.get_activities(
            collection=patient_collection
        )
        if "valueId" not in activity_current
    ]

    for other_activity, activity_matching_value_id in zip(
        other_activities, activities_matching_value_id
    ):
        assert other_activity["_rev"] == activity_matching_value_id["_rev"] + 1
        assert "valueId" not in other_activity

        del other_activity["_id"]
        del activity_matching_value_id["_id"]
        del other_activity["_rev"]
        del activity_matching_value_id["_rev"]
        del activity_matching_value_id["valueId"]

    assert other_activities == activities_matching_value_id
