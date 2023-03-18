# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
from pathlib import Path

from scope.documents.document_set import datetime_from_document, DocumentSet
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

        patient_collection = _migrate_assessment_log_with_embedded_assessment(
            collection=patient_collection,
        )
        patient_collection = _migrate_scheduled_activity_remove_reminder(
            collection=patient_collection,
        )
        patient_collection = _migrate_scheduled_activity_snapshot(
            collection=patient_collection,
        )
        patient_collection = _migrate_activity_log_snapshot(
            collection=patient_collection,
        )

        archive.replace_collection_documents(
            collection=patients_document_current["collection"],
            document_set=patient_collection,
        )

    return archive


def _migrate_assessment_log_with_embedded_assessment(
    collection: DocumentSet,
) -> DocumentSet:
    """
    Some assessmentLog documents have an embedded assessment.
    These resulted from early experimentation in developing snapshots.
    """

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

    print("  Updated {:4} documents: {}.".format(
        len(documents_original),
        "migrate_assessment_log_with_embedded_assessment",
    ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_remove_reminder(
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove reminder fields from any scheduled activity.
    """
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

    print("  Updated {:4} documents: {}.".format(
        len(documents_original),
        "migrate_scheduled_activity_remove_reminder",
    ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_snapshot(
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any scheduled activity that does not have one.
    """

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

    print("  Updated {:4} documents: {}.".format(
        len(documents_original),
        "migrate_scheduled_activity_snapshot",
    ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_activity_log_snapshot(
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any activity log that does not have one.
    """

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

    print("  Updated {:4} documents: {}.".format(
        len(documents_original),
        "migrate_activity_log_snapshot",
    ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )

# # Allow typing to forward reference
# # TODO: Not necessary with Python 3.11
# from __future__ import annotations
#
# import copy
# from pathlib import Path
# from typing import Dict
#
# import scope.populate.data.archive
#
#
# def archive_migrate_v0_7_0(
#     *,
#     archive: scope.populate.data.archive.Archive,
# ) -> scope.populate.data.archive.Archive:
#     #
#     # Migration for schema modifications in #354
#     # https://github.com/uwscope/scope-web/pull/354
#     #
#     migrated_entries: Dict[Path, dict] = {}
#     for (path_current, document_current) in archive.entries.items():
#         path_current = copy.deepcopy(path_current)
#         document_current = copy.deepcopy(document_current)
#
#         # #354 migration applies to activity documents
#         if document_current["_type"] == "activity":
#             # Ensure "hasReminder" is always False
#             document_current["hasReminder"] = False
#             # Remove any "reminderTimeOfDay"
#             if "reminderTimeOfDay" in document_current:
#                 del document_current["reminderTimeOfDay"]
#         # #354 migration applies to scheduledActivity documents
#         if document_current["_type"] == "scheduledActivity":
#             # Remove any "reminderDate"
#             if "reminderDate" in document_current:
#                 del document_current["reminderDate"]
#             # Remove any "reminderDateTime"
#             if "reminderDateTime" in document_current:
#                 del document_current["reminderDateTime"]
#             # Remove any "reminderTimeOfDay"
#             if "reminderTimeOfDay" in document_current:
#                 del document_current["reminderTimeOfDay"]
#
#         migrated_entries[path_current] = document_current
#
#     return scope.populate.data.archive.Archive(entries=migrated_entries)
