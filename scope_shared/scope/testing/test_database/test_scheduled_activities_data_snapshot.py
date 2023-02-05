"""
In addition to its standard set properties,
a put to scope.database.patient.activity_logs must maintain the scheduled activity.
"""

import pytest
import pprint
from typing import Callable


import scope.database.collection_utils as collection_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.scheduled_activities
import scope.database.patient.values
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient


def test_scheduled_activities_build_data_snapshot(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_factory: Callable[[], dict],
    data_fake_scheduled_activity_factory: Callable[[], dict],
    data_fake_value_factory: Callable[[], dict],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake scheduled activity
    fake_scheduled_activity = data_fake_scheduled_activity_factory()

    # Obtain fake activity and store in db
    fake_activity = data_fake_activity_factory()
    fake_activity_set_post_result = scope.database.patient.activities.post_activity(
        collection=patient_collection, activity=fake_activity
    )
    assert fake_activity_set_post_result.inserted_count == 1
    inserted_fake_activity = fake_activity_set_post_result.document

    # Obtain fake value and store in db
    fake_value = data_fake_value_factory()
    fake_value_set_post_result = scope.database.patient.values.post_value(
        collection=patient_collection, value=fake_value
    )
    assert fake_value_set_post_result.inserted_count == 1
    inserted_fake_value = fake_value_set_post_result.document

    fake_scheduled_activity[
        scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
    ].update(
        {
            scope.database.patient.activities.DOCUMENT_TYPE: inserted_fake_activity,
            scope.database.patient.values.DOCUMENT_TYPE: inserted_fake_value,
        }
    )

    fake_scheduled_activity_post_result = (
        scope.database.patient.scheduled_activities.post_scheduled_activity(
            collection=patient_collection, scheduled_activity=fake_scheduled_activity
        )
    )
    assert fake_scheduled_activity_post_result.inserted_count == 1
    inserted_fake_scheduled_activity = fake_scheduled_activity_post_result.document

    # Update and put value
    inserted_fake_value.update({"name": "update fake value"})
    del inserted_fake_value["_id"]
    collection_utils.put_set_element(
        collection=patient_collection,
        document_type=scope.database.patient.values.DOCUMENT_TYPE,
        semantic_set_id=scope.database.patient.values.SEMANTIC_SET_ID,
        set_id=inserted_fake_value["_set_id"],
        document=inserted_fake_value,
    )

    # Get the updated value
    updated_fake_value = scope.database.patient.values.get_value(
        collection=patient_collection, set_id=inserted_fake_value["_set_id"]
    )

    new_data_snapshot = (
        scope.database.patient.scheduled_activities._build_data_snapshot(
            collection=patient_collection,
            scheduled_activity=inserted_fake_scheduled_activity,
        )
    )

    scope.schema_utils.assert_schema(
        data=new_data_snapshot,
        schema=scope.schema.scheduled_activity_data_snapshot_schema,
        expected_valid=True,
    )

    assert (
        new_data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE]
        == inserted_fake_activity
    )

    assert (
        new_data_snapshot[scope.database.patient.values.DOCUMENT_TYPE]
        == updated_fake_value
    )

    # Update and put activity
    inserted_fake_activity.update({"name": "update fake activity"})
    del inserted_fake_activity["_id"]
    collection_utils.put_set_element(
        collection=patient_collection,
        document_type=scope.database.patient.activities.DOCUMENT_TYPE,
        semantic_set_id=scope.database.patient.activities.SEMANTIC_SET_ID,
        set_id=inserted_fake_activity["_set_id"],
        document=inserted_fake_activity,
    )

    # Get the updated activity
    updated_fake_activity = scope.database.patient.activities.get_activity(
        collection=patient_collection, set_id=inserted_fake_activity["_set_id"]
    )

    new_data_snapshot = (
        scope.database.patient.scheduled_activities._build_data_snapshot(
            collection=patient_collection,
            scheduled_activity=inserted_fake_scheduled_activity,
        )
    )

    scope.schema_utils.assert_schema(
        data=new_data_snapshot,
        schema=scope.schema.scheduled_activity_data_snapshot_schema,
        expected_valid=True,
    )

    assert (
        new_data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE]
        == updated_fake_activity
    )

    assert (
        new_data_snapshot[scope.database.patient.values.DOCUMENT_TYPE]
        == updated_fake_value
    )
