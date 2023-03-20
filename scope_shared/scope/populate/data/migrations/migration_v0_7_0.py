# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
import datetime
from pathlib import Path

from scope.database import collection_utils, date_utils
from scope.documents.document_set import datetime_from_document, document_id_from_datetime, DocumentSet
import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def archive_migrate_v0_7_0(
    *,
    archive_path: Path,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
    print("Migrating to v0.7.0.")

    #
    # These specific collections in the dev database are leftovers from testing, delete them
    #
    if archive_path.name.startswith("archive_dev_v0.7.0_"):
        delete_collections = [
            'patient_eqy3qm5xvguvk',
            'patient_efbavfkbwjm6w',
            'patient_psfy75n7irege',
        ]

        delete_documents = []
        for delete_collection_current in delete_collections:
            delete_documents.extend(archive.collection_documents(collection=delete_collection_current))

        migrated_entries = {
            key_current: document_current
            for (key_current, document_current) in archive.entries.items()
            if document_current not in delete_documents
        }

        print("Deleted {} collections totaling {} documents.".format(
            len(delete_collections),
            len(archive.entries) - len(migrated_entries),
        ))

        archive = scope.populate.data.archive.Archive(entries=migrated_entries)

    #
    # Go through each patient collection
    #
    patients_documents = archive.patients_documents(
        remove_sentinel=True,
        remove_revisions=True,
    )

    for patients_document_current in patients_documents:
        print("Migrating patient '{}'.".format(patients_document_current["name"]))

        patient_collection = archive.collection_documents(
            collection=patients_document_current["collection"],
        )

        # Cleaning up individual fields
        patient_collection = _migrate_assessment_log_with_embedded_assessment(
            collection=patient_collection,
        )
        patient_collection = _migrate_activity_remove_reminder(
            collection=patient_collection,
        )
        patient_collection = _migrate_scheduled_activity_remove_reminder(
            collection=patient_collection,
        )

        # Set aside documents in the old activity format
        patient_collection = _migrate_activity_rename_type_old_format(
            collection=patient_collection,
        )
        # Refactor values and activities out of values inventory
        patient_collection = _migrate_values_inventory_refactor_values_and_activities(
            collection=patient_collection,
        )

        archive.replace_collection_documents(
            collection=patients_document_current["collection"],
            document_set=patient_collection,
        )

    return archive


def _migrate_activity_rename_type_old_format(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Renames the type of existing activities.

    This gets them out of the way while we create activities from the values inventory.
    """

    print("  migrate_activity_rename_type_old_format")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Presence of "startDateTime" indicates this activity
        # is in the old format that includes an embedded schedule
        if "startDateTime" in document_migrated:
            is_migrated = True

            document_migrated["_type"] = "activity_OldFormat"

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_activity_remove_reminder(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove reminder fields from any activity.
    """

    print("  migrate_activity_remove_reminder")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Ensure "hasReminder" is always False
        if document_migrated["hasReminder"]:
            is_migrated = True

            document_migrated["hasReminder"] = False

        # Remove any "reminderTimeOfDay"
        if "reminderTimeOfDay" in document_migrated:
            is_migrated = True

            del document_migrated["reminderTimeOfDay"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_activity_log_snapshot(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any activity log that does not have one.
    """

    print("  migrate_activity_log_snapshot")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activityLog",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Including the snapshot led to removal of several incomplete fields
        if "activityId" in document_migrated:
            is_migrated = True

            del document_migrated["activityId"]

        if "activityName" in document_migrated:
            is_migrated = True

            del document_migrated["activityName"]

        # completed was determined to be redundant with existence of the log
        if "completed" in document_migrated:
            is_migrated = True

            del document_migrated["completed"]

        # Development included experimentation with an embedded activity document
        if "activity" in document_migrated:
            is_migrated = True

            del document_migrated["activity"]

        # Schema was enhanced to enforce that success No disallows alternative
        # Prior to that the client was storing empty strings
        if document_migrated["success"] == "No":
            if "alternative" in document_migrated:
                is_migrated = True

                assert document_migrated["alternative"] == ""
                del document_migrated["alternative"]

        # Development included generation of some snapshots that
        # captured the scheduledActivity before marking it complete
        if "dataSnapshot" in document_migrated:
            if "scheduledActivity" in document_migrated["dataSnapshot"]:
                if not document_migrated["dataSnapshot"]["scheduledActivity"]["completed"]:
                    is_migrated = True

                    # We expect only two instances of this,
                    # pay attention if we unexpectedly see other instances
                    assert document_migrated["_id"] in [
                        "63eea4a7ac019fe9b4bc07cc",
                        "63efc99eac019fe9b4bc08d2",
                    ]
                    del document_migrated["dataSnapshot"]["scheduledActivity"]

        if "dataSnapshot" not in document_migrated:
            is_migrated = True

            document_migrated["dataSnapshot"] = {}

        if "scheduledActivity" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["scheduledActivity"] = collection.filter_match(
                match_type="scheduledActivity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "scheduledActivityId": document_migrated["scheduledActivityId"]
                }
            ).unique()

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_log_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_assessment_log_with_embedded_assessment(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Some assessmentLog documents have an embedded assessment.
    These resulted from early experimentation in developing snapshots.
    """

    print("  migrate_assessment_log_with_embedded_assessment")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="assessmentLog",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        if "assessment" in document_migrated:
            is_migrated = True

            # We expect only one instance of this,
            # pay attention if we unexpectedly see other instances
            assert document_migrated["_id"] in [
                "63d04ccf30b3259d115d7503",
            ]

            document_migrated["assessmentId"] = document_migrated["assessment"]["assessmentId"]
            del document_migrated["assessment"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.assessment_log_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_remove_reminder(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove reminder fields from any scheduled activity.
    """

    print("  migrate_scheduled_activity_remove_reminder")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Remove any "reminderDate"
        if "reminderDate" in document_migrated:
            is_migrated = True

            del document_migrated["reminderDate"]

        # Remove any "reminderDateTime"
        if "reminderDateTime" in document_migrated:
            is_migrated = True

            del document_migrated["reminderDateTime"]

        # Remove any "reminderTimeOfDay"
        if "reminderTimeOfDay" in document_migrated:
            is_migrated = True

            del document_migrated["reminderTimeOfDay"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.scheduled_activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_snapshot(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any scheduled activity that does not have one.
    """

    print("  migrate_scheduled_activity_snapshot")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        if "dataSnapshot" not in document_migrated:
            is_migrated = True

            document_migrated["dataSnapshot"] = {}

        if "activitySchedule" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["activitySchedule"] = collection.filter_match(
                match_type="activitySchedule",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "activityScheduleId": document_migrated["activityScheduleId"]
                }
            ).unique()

        if "activity" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["activity"] = collection.filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "activityId": document_migrated["dataSnapshot"]["activitySchedule"]["activityId"]
                }
            ).unique()

        if "valueId" in document_migrated["dataSnapshot"]["activity"]:
            if "value" not in document_migrated["dataSnapshot"]:
                is_migrated = True

                document_migrated["dataSnapshot"]["value"] = collection.filter_match(
                    match_type="value",
                    match_deleted=False,
                    match_datetime_at=datetime_from_document(document=document_migrated),
                    match_values={
                        "valueId": document_migrated["dataSnapshot"]["activity"]["valueId"]
                    }
                ).unique()

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.scheduled_activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_values_inventory_refactor_values_and_activities(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove values and activities from values inventory and refactor them into documents.

    This steps through the ordered sequence of values inventory documents.
    At each document, values and activities created for previous documents therefore exist.
    """

    print("  migrate_values_inventory_refactor_values_and_activities")

    # Performance optimization
    documents_filtered_relevant = collection.filter_match(
        match_type="valuesInventory",
    ).union(
        documents=collection.filter_match(
            match_type="value",
        ),
    ).union(
        documents=collection.filter_match(
            match_type="activity",
        ),
    )

    # For each value and activity, createdDateTime functions as a de facto unique id.
    # We need to be able to look these up in both directions.
    value_id_by_created_datetime = {}
    created_datetime_by_value_id = {}
    activity_id_by_created_datetime = {}
    created_datetime_by_activity_id = {}

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    documents_created = []
    for document_current in documents_filtered_relevant.filter_match(
        match_type="valuesInventory",
        match_deleted=False,
    ).order_by_revision():
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Presence of "values" indicates the old format
        if "values" in document_migrated:
            is_migrated = True

            # The createdDateTime of all currently existing values
            document_migrated_values_created_datetimes = [
                value_entry_current["createdDateTime"]
                for value_entry_current in document_migrated["values"]
            ]
            # createdDateTime will always be unique within a set of values
            assert len(document_migrated_values_created_datetimes) == len(set(document_migrated_values_created_datetimes))

            # The createdDateTime of all currently existing activities
            document_migrated_activities_created_datetimes = []
            for value_entry_current in document_migrated["values"]:
                for activity_entry_current in value_entry_current["activities"]:
                    document_migrated_activities_created_datetimes.append(activity_entry_current["createdDateTime"])
            # createdDateTime will always be unique within a set of activities
            assert len(document_migrated_activities_created_datetimes) == len(set(document_migrated_activities_created_datetimes))

            #
            # Values existing at the beginning of this migration step
            #
            values_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="value",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )

            #
            # Delete any values that no longer exist
            #
            for value_document_current in values_existing:
                created_datetime = created_datetime_by_value_id[value_document_current["valueId"]]
                if created_datetime not in document_migrated_values_created_datetimes:
                    print("  - Delete Value:")
                    print("    + Was: {}".format(value_document_current["name"]))

                    document_value_deleted = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "value",
                        "_set_id": value_document_current["_set_id"],
                        "_rev": value_document_current["_rev"] + 1,
                        "_deleted": True,
                    }

                    scope.schema_utils.assert_schema(
                        data=document_value_deleted,
                        schema=scope.schema.set_tombstone_schema,
                    )

                    documents_created.append(document_value_deleted)

            #
            # Create/Maintain any values in this values inventory document
            #
            for value_entry_current in document_migrated["values"]:
                if value_entry_current["createdDateTime"] not in value_id_by_created_datetime:
                    # Creating a new value
                    print("  - Create Value:")
                    print("    + Now: {}".format(value_entry_current["name"]))

                    # Generate a new value id
                    value_id = collection_utils.generate_set_id()

                    # Maintain our maps in both directions
                    value_id_by_created_datetime[value_entry_current["createdDateTime"]] = value_id
                    created_datetime_by_value_id[value_id] = value_entry_current["createdDateTime"]

                    value_document_created = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "value",
                        "_set_id": value_id,
                        "_rev": 1,
                        "valueId": value_id,
                        "name": value_entry_current["name"],
                        "lifeAreaId": value_entry_current["lifeareaId"],
                        "editedDateTime": value_entry_current["editedDateTime"],
                    }

                    scope.schema_utils.assert_schema(
                        data=value_document_created,
                        schema=scope.schema.value_schema,
                    )

                    documents_created.append(value_document_created)
                else:
                    # Maintaining an existing value
                    value_id = value_id_by_created_datetime[value_entry_current["createdDateTime"]]

                    value_document_current = values_existing.filter_match(
                        match_values={
                            "valueId": value_id,
                        }
                    ).unique()

                    value_document_changed = (
                        value_document_current["name"] != value_entry_current["name"]
                        or value_document_current["lifeAreaId"] != value_entry_current["lifeareaId"]
                    )

                    if value_document_changed:
                        print("  - Update Value:")
                        print("    + Now: {}".format(value_entry_current["name"]))
                        print("    + Was: {}".format(value_document_current["name"]))

                        value_document_created = {
                            "_id": document_id_from_datetime(
                                generation_time=datetime_from_document(
                                    document=document_migrated,
                                )
                            ),
                            "_type": "value",
                            "_set_id": value_document_current["_set_id"],
                            "_rev": value_document_current["_rev"] + 1,
                            "valueId": value_document_current["valueId"],
                            "name": value_entry_current["name"],
                            "lifeAreaId": value_entry_current["lifeareaId"],
                            "editedDateTime": value_entry_current["editedDateTime"],
                        }

                        scope.schema_utils.assert_schema(
                            data=value_document_created,
                            schema=scope.schema.value_schema,
                        )

                        documents_created.append(value_document_created)

            #
            # The two representations of values should now be the same
            #
            values_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="value",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )
            original_values_tuples = [
                (value_entry_current["lifeareaId"], value_entry_current["name"])
                for value_entry_current in document_migrated["values"]
            ]
            migrated_values_tuples = [
                (value_document_current["lifeAreaId"], value_document_current["name"])
                for value_document_current in values_existing
            ]

            assert len(original_values_tuples) == len(migrated_values_tuples)
            assert set(original_values_tuples) == set(migrated_values_tuples)

            #
            # Activities existing at the beginning of this migration step
            #
            activities_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )

            #
            # Delete any activities that no longer exist
            #
            for activity_document_current in activities_existing:
                created_datetime = created_datetime_by_activity_id[activity_document_current["activityId"]]
                if created_datetime not in document_migrated_activities_created_datetimes:
                    print("  - Delete Activity:")
                    print("    + Was: {}".format(activity_document_current["name"]))

                    document_activity_deleted = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "activity",
                        "_set_id": activity_document_current["_set_id"],
                        "_rev": activity_document_current["_rev"] + 1,
                        "_deleted": True,
                    }

                    scope.schema_utils.assert_schema(
                        data=document_activity_deleted,
                        schema=scope.schema.set_tombstone_schema,
                    )

                    documents_created.append(document_activity_deleted)

            #
            # Create/Maintain any values in this values inventory document
            #
            for value_entry_current in document_migrated["values"]:
                value_document_current = values_existing.filter_match(
                    match_values={
                        "valueId": value_id_by_created_datetime[value_entry_current["createdDateTime"]],
                    }
                ).unique()

                for activity_entry_current in value_entry_current["activities"]:
                    if activity_entry_current["createdDateTime"] not in activity_id_by_created_datetime:
                        # Creating a new activity
                        print("  - Create Activity:")
                        print("    + Now: {}".format(activity_entry_current["name"]))
                        print("           E: {} / I: {}".format(
                            activity_entry_current["enjoyment"],
                            activity_entry_current["importance"],
                        ))

                        # Generate a new activity id
                        activity_id = collection_utils.generate_set_id()

                        # Maintain our maps in both directions
                        activity_id_by_created_datetime[activity_entry_current["createdDateTime"]] = activity_id
                        created_datetime_by_activity_id[activity_id] = activity_entry_current["createdDateTime"]

                        activity_document_created = {
                            "_id": document_id_from_datetime(
                                generation_time=datetime_from_document(
                                    document=document_migrated,
                                )
                            ),
                            "_type": "activity",
                            "_set_id": activity_id,
                            "_rev": 1,
                            "activityId": activity_id,
                            "name": activity_entry_current["name"],
                            "enjoyment": activity_entry_current["enjoyment"],
                            "importance": activity_entry_current["importance"],
                            "valueId": value_document_current["valueId"],
                            "editedDateTime": activity_entry_current["editedDateTime"],
                        }

                        scope.schema_utils.assert_schema(
                            data=activity_document_created,
                            schema=scope.schema.activity_schema,
                        )

                        documents_created.append(activity_document_created)
                    else:
                        # Maintaining an existing activity
                        activity_document_current = activities_existing.filter_match(
                            match_values={
                                "activityId": activity_id_by_created_datetime[activity_entry_current["createdDateTime"]]
                            }
                        ).unique()

                        activity_document_changed = (
                            activity_document_current["name"] != activity_entry_current["name"]
                            or activity_document_current["enjoyment"] != activity_entry_current["enjoyment"]
                            or activity_document_current["importance"] != activity_entry_current["importance"]
                        )

                        if activity_document_changed:
                            print("  - Update Activity:")
                            print("    + Now: {}".format(activity_entry_current["name"]))
                            print("           E: {} / I: {}".format(
                                activity_entry_current["enjoyment"],
                                activity_entry_current["importance"],
                            ))
                            print("    + Was: {}".format(activity_document_current["name"]))
                            print("           E: {} / I: {}".format(
                                activity_document_current["enjoyment"],
                                activity_document_current["importance"],
                            ))

                            activity_document_created = {
                                "_id": document_id_from_datetime(
                                    generation_time=datetime_from_document(
                                        document=document_migrated,
                                    )
                                ),
                                "_type": "activity",
                                "_set_id": activity_document_current["_set_id"],
                                "_rev": activity_document_current["_rev"] + 1,
                                "activityId": activity_document_current["activityId"],
                                "name": activity_entry_current["name"],
                                "enjoyment": activity_entry_current["enjoyment"],
                                "importance": activity_entry_current["importance"],
                                "valueId": value_document_current["valueId"],
                                "editedDateTime": activity_entry_current["editedDateTime"],
                            }

                            scope.schema_utils.assert_schema(
                                data=activity_document_created,
                                schema=scope.schema.activity_schema,
                            )

                            documents_created.append(activity_document_created)

            #
            # The two representations of activities should now be the same
            #
            activities_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )
            original_activities_tuples = []
            for value_entry_current in document_migrated["values"]:
                for activity_entry_current in value_entry_current["activities"]:
                    original_activities_tuples.append((
                        activity_entry_current["name"],
                        activity_entry_current["enjoyment"],
                        activity_entry_current["importance"],
                        value_entry_current["name"],
                        value_entry_current["lifeareaId"],
                    ))

            migrated_activities_tuples = []
            for activity_document_current in activities_existing:
                value_document_current = values_existing.filter_match(
                    match_values={
                        "valueId": activity_document_current["valueId"],
                    },
                ).unique()

                migrated_activities_tuples.append((
                    activity_document_current["name"],
                    activity_document_current["enjoyment"],
                    activity_document_current["importance"],
                    value_document_current["name"],
                    value_document_current["lifeAreaId"],
                ))

            assert len(original_activities_tuples) == len(migrated_activities_tuples)
            assert set(original_activities_tuples) == set(migrated_activities_tuples)

            #
            # Migrated fields can now be removed from the values inventory
            #
            del document_migrated["values"]
            del document_migrated["lastUpdatedDateTime"]

        if is_migrated:
            scope.schema_utils.assert_schema(
                data=document_migrated,
                schema=scope.schema.values_inventory_schema,
            )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))
    if len(documents_created):
        print("  - Created {} documents.".format(
            len(documents_created),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    ).union(
        documents=documents_created,
    )
