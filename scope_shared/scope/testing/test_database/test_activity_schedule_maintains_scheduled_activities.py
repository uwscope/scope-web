"""
In addition to its standard set properties,
a put or post to scope.database.patient.activities must maintain the scheduled activities.
"""

import datetime
import pytz
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activity_schedules
import scope.database.patient.scheduled_activities
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient


def test_activity_schedule_calculate_scheduled_activities_to_create():
    time_of_day = 8

    activity_schedule = {
        "_type": "activitySchedule",
        "activityId": "testActivityId",
        "isActive": True,
        "isDeleted": False,
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(datetime.datetime(2022, 3, 12, 6))
        ),
        "startDateTime": date_utils.format_datetime(
            pytz.utc.localize(datetime.datetime(2022, 3, 12, 6))
        ),
        "hasRepetition": True,
        "repeatDayFlags": {
            scope.enums.DayOfWeek.Monday.value: True,
            scope.enums.DayOfWeek.Tuesday.value: True,
            scope.enums.DayOfWeek.Wednesday.value: False,
            scope.enums.DayOfWeek.Thursday.value: False,
            scope.enums.DayOfWeek.Friday.value: False,
            scope.enums.DayOfWeek.Saturday.value: False,
            scope.enums.DayOfWeek.Sunday.value: False,
        },
        "timeOfDay": time_of_day,
        "hasReminder": False,
        # "reminderTimeOfDay": time_of_day,
    }
    scope.schema_utils.assert_schema(
        data=activity_schedule,
        schema=scope.schema.activity_schedule_schema,
        expected_valid=True,
    )

    scheduled_activities = scope.database.patient.activity_schedules._calculate_scheduled_activities_to_create(
        activity_schedule_id="testActivityScheduleId",
        activity_schedule=activity_schedule,
        maintenance_datetime=pytz.utc.localize(datetime.datetime(2022, 3, 14, 10)),
    )
    scope.schema_utils.assert_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
        expected_valid=True,
    )

    scheduled_dates = []
    scheduled_dates.extend(
        [datetime.date(2022, 3, day) for day in list([14, 15, 21, 22, 28, 29])]
    )
    scheduled_dates.extend(
        [datetime.date(2022, 4, day) for day in list([4, 5, 11, 12, 18, 19, 25, 26])]
    )
    scheduled_dates.extend(
        [
            datetime.date(2022, 5, day)
            for day in list([2, 3, 9, 10, 16, 17, 23, 24, 30, 31])
        ]
    )
    scheduled_dates.extend(
        [datetime.date(2022, 6, day) for day in list([6, 7, 13, 14])]
    )

    assert scheduled_activities == [
        {
            "_type": "scheduledActivity",
            "activityScheduleId": "testActivityScheduleId",
            "completed": False,
            "dueDate": date_utils.format_date(scheduled_date_current),
            "dueTimeOfDay": time_of_day,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime.datetime(
                        scheduled_date_current.year,
                        scheduled_date_current.month,
                        scheduled_date_current.day,
                        15,
                    )
                )
            ),
            # "reminderDate": date_utils.format_date(scheduled_date_current),
            # "reminderTimeOfDay": time_of_day,
            # "reminderDateTime": date_utils.format_datetime(
            #     pytz.utc.localize(
            #         datetime.datetime(
            #             scheduled_date_current.year,
            #             scheduled_date_current.month,
            #             scheduled_date_current.day,
            #             15,
            #         )
            #     )
            # ),
        }
        for scheduled_date_current in scheduled_dates
    ]


def test_activity_schedule_calculate_scheduled_activities_to_delete():
    scheduled_activities = [
        {  # Different activityScheduleId, should not be deleted, even in future
            "_type": "scheduledActivity",
            "activityScheduleId": "differentId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 8,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 8))
            ),
            "completed": False,
        },
        {  # Past item (previous date, later time), should not be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 12)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 12, 16))
            ),
            "completed": False,
        },
        {  # Past item (same date, previous time), should not be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 8,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 8))
            ),
            "completed": False,
        },
        {  # Future item (same date, later time), already completed, should not be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": True,
        },
        {  # Future item (later date, earlier time), already completed, should not be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": True,
        },
        {  # Future item (same date, later time), should be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": False,
        },
        {  # Future item (later date, earlier time), should be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": False,
        },
    ]
    scope.schema_utils.assert_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
        expected_valid=True,
    )

    deleted_activities = scope.database.patient.activity_schedules._calculate_scheduled_activities_to_delete(
        activity_schedule_id="deleteTestId",
        scheduled_activities=scheduled_activities,
        maintenance_datetime=pytz.utc.localize(
            datetime.datetime(2022, 3, 13, 12, 0, 0)
        ),
    )

    assert deleted_activities == [
        {  # Future item (same date, later time), should be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": False,
        },
        {  # Future item (later date, earlier time), should be deleted
            "_type": "scheduledActivity",
            "activityScheduleId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": False,
        },
    ]


def test_activity_schedule_put_maintains_scheduled_activities(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_schedule_factory: Callable[[], dict],
):
    """
    Test that the scheduled activities are maintained.

    The actual logic of scheduling specific activities is tested elsewhere.
    This test just ensures that it sees the collection being manipulated.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake activity schedule to use as template
    fake_activity_schedule = data_fake_activity_schedule_factory()
    activity_schedule_id = collection_utils.generate_set_id()
    fake_activity_schedule[
        scope.database.patient.activity_schedules.SEMANTIC_SET_ID
    ] = activity_schedule_id
    fake_activity_schedule["_set_id"] = activity_schedule_id

    # Disable the activity schedule
    fake_activity_schedule.update(
        {
            "isActive": False,
            "isDeleted": False,
            "startDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity_schedule(
        collection=patient_collection,
        set_id=activity_schedule_id,
        activity_schedule_complete=fake_activity_schedule,
    )

    # Determine what scheduled activities already exist
    existing_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    if not existing_scheduled_activities:
        existing_scheduled_activities = []

    # Enable the activity schedule
    fake_activity_schedule.update(
        {
            "isActive": True,
            "isDeleted": False,
            "startDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity_schedule(
        collection=patient_collection,
        set_id=activity_schedule_id,
        activity_schedule_complete=fake_activity_schedule,
    )

    # Ensure we now obtain new scheduled activities
    new_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    new_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in new_scheduled_activities
        if scheduled_activity_current not in existing_scheduled_activities
    ]
    assert len(new_scheduled_activities) > 0

    # Disable the activity of the activity schedule
    fake_activity_schedule.update(
        {
            "isActive": False,
            "isDeleted": False,
            "startDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity_schedule(
        collection=patient_collection,
        set_id=activity_schedule_id,
        activity_schedule_complete=fake_activity_schedule,
    )

    # Ensure there are no pending scheduled activities
    # Because pending logic is already tested,
    # this confirms cancellation while being robust to an item created in this test which is now in the past
    existing_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    if not existing_scheduled_activities:
        existing_scheduled_activities = []

    existing_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in existing_scheduled_activities
        if scheduled_activity_current[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ]
        == activity_schedule_id
    ]

    pending_scheduled_activities = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=existing_scheduled_activities,
        after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
    )

    assert len(pending_scheduled_activities) == 0

    # Enable the activity schedule
    fake_activity_schedule.update(
        {
            "isActive": True,
            "isDeleted": False,
            "startDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity_schedule(
        collection=patient_collection,
        set_id=activity_schedule_id,
        activity_schedule_complete=fake_activity_schedule,
    )

    # Ensure we now obtain new scheduled activities
    new_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    new_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in new_scheduled_activities
        if scheduled_activity_current not in existing_scheduled_activities
    ]
    assert len(new_scheduled_activities) > 0

    # Delete the activity schedule
    fake_activity_schedule.update(
        {
            "isActive": True,
            "isDeleted": True,
            "startDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity_schedule(
        collection=patient_collection,
        set_id=activity_schedule_id,
        activity_schedule_complete=fake_activity_schedule,
    )

    # Ensure there are no pending scheduled activities
    # Because pending logic is already tested,
    # this confirms cancellation while being robust to an item created in this test which is now in the past
    existing_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    if not existing_scheduled_activities:
        existing_scheduled_activities = []

    existing_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in existing_scheduled_activities
        if scheduled_activity_current[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ]
        == activity_schedule_id
    ]

    pending_scheduled_activities = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=existing_scheduled_activities,
        after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
    )

    assert len(pending_scheduled_activities) == 0