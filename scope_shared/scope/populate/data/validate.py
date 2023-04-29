# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

from scope.documents.document_set import datetime_from_document, DocumentSet
import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def validate_archive(
    *,
    archive: scope.populate.data.archive.Archive,
):
    # Validate that expected collections exist
    print("Validating archive patients structure.")
    _validate_archive_expected_collections(archive=archive)

    # Validate every document matches the document schema
    print("Validating document schemas.")
    _validate_archive_document_schema(archive=archive)

    # Go through each patient collection, validate contents of each patient collection
    patients_documents = archive.patients_documents(
        remove_sentinel=True,
        remove_revisions=True,
    )
    for patients_document_current in patients_documents:
        print("Validating patient '{}'.".format(patients_document_current["name"]))

        patient_collection_current = archive.collection_documents(
            collection=patients_document_current["collection"]
        )

        _validate_patient_collection(collection=patient_collection_current)


def _validate_archive_document_schema(
    *,
    archive: scope.populate.data.archive.Archive,
):
    """
    Validate every document matches the document schema.
    """

    for document_current in archive.entries.values():
        # Assert the document schema
        scope.schema_utils.assert_schema(
            data=document_current,
            schema=scope.schema.document_schema,
        )

        # These are currently not enforced by the schema
        if not document_current.get("_deleted"):
            if document_current["_type"] == "activityLog":
                # Cannot be included because of test framework
                assert "scheduledActivity" in document_current["dataSnapshot"]
                # Should always be true but not tested by schema
                assert document_current["dataSnapshot"]["scheduledActivity"][
                    "completed"
                ]
            if document_current["_type"] == "scheduledActivity":
                # Cannot be included because of test framework
                assert "activity" in document_current["dataSnapshot"]


def _validate_archive_expected_collections(
    *,
    archive: scope.populate.data.archive.Archive,
):
    """
    Validate archive contains expected collections.
    """

    # We expect every collection to be referenced
    unreferenced_collections = archive.collections()
    assert "patients" in unreferenced_collections
    unreferenced_collections.remove("patients")
    assert "providers" in unreferenced_collections
    unreferenced_collections.remove("providers")

    # Ensure every referenced patient collection exists
    patients_documents = archive.patients_documents(
        remove_sentinel=True,
        remove_revisions=True,
    )

    for patients_document_current in patients_documents:
        # Ensure these documents cannot be deleted
        # TODO: This is also implied by the schema.
        #       If we had a cleaner hierarchy of schemas, it could be more explicit and this could be removed.
        assert "_deleted" not in patients_document_current

        # Track that each referenced collection exists and is referenced exactly once
        referenced_collection_current = patients_document_current["collection"]
        assert referenced_collection_current in unreferenced_collections
        unreferenced_collections.remove(referenced_collection_current)

    # Every collection should now have been referenced
    assert len(unreferenced_collections) == 0


def _validate_patient_collection(
    *,
    collection: DocumentSet,
):
    """
    Validate the entire set of documents in a patient collection.
    """

    _validate_patient_collection_documents(collection=collection)
    _validate_patient_collection_strings(collection=collection)

    _validate_patient_collection_activity(collection=collection)
    _validate_patient_collection_activity_logs(collection=collection)
    _validate_patient_collection_activity_schedules(collection=collection)
    _validate_patient_collection_scheduled_activities(collection=collection)
    _validate_patient_collection_values(collection=collection)


def _validate_patient_collection_documents(
    *,
    collection: DocumentSet,
):
    """
    Validate the core properties of documents.
    """

    # Every document must have a unique id
    existing_document_ids = []
    for document_current in collection:
        assert document_current["_id"] not in existing_document_ids
        existing_document_ids.append(document_current["_id"])

    # Set types must have matching _set_id and semantic id
    for document_current in collection:
        if document_current["_type"] in [
            "activityLog",
            "activitySchedule",
            "activity",
            "assessmentLog",
            "assessment",
            "caseReview",
            "moodLog",
            "scheduledActivity",
            "scheduledAssessment",
            "session",
            "value",
        ]:
            if "_deleted" in document_current:
                assert document_current["_deleted"]
                assert "_set_id" in document_current
            else:
                assert (
                    document_current["_set_id"]
                    == document_current["{}Id".format(document_current["_type"])]
                )
        else:
            assert "_set_id" not in document_current

    # Every document key must be unique, with incrementing revisions, with monotonically increasing times.
    # Any deletion must be the final revision in a sequence.
    for revisions_current in collection.group_revisions().values():
        # If two documents have the same key,
        # they'll be grouped into the same revision sequence.
        # Two documents would therefore have _rev of 1.
        # This would also be caught in the next loop,
        # but is explicitly tested here for clarity in case of failure.
        assert revisions_current.filter_match(match_values={"_rev": 1}).is_unique()

        document_previous = None
        for index, document_current in enumerate(revisions_current.order_by_revision()):
            # Revisions must have an incrementing sequence of _rev values
            assert document_current["_rev"] == index + 1

            # Any deletion cannot be the first revision and must be the final revision
            if "_delete" in document_current:
                assert "_rev" != 1
                assert "_rev" == len(revisions_current)

            # Times must be monotonically increasing.
            if document_previous:
                assert datetime_from_document(
                    document=document_current
                ) >= datetime_from_document(document=document_previous)

            document_previous = document_current


def _validate_patient_collection_strings(
    *,
    collection: DocumentSet,
):
    """
    Validate properties of strings in specific documents.
    """

    activity_documents = collection.filter_match(
        match_type="activity",
        match_deleted=False,
    )
    value_documents = collection.filter_match(
        match_type="value",
        match_deleted=False,
    )

    # Activity names must already be trimmed
    for document_current in activity_documents:
        assert document_current["name"] == document_current["name"].strip()

    # Value names must already be trimmed
    for document_current in value_documents:
        if document_current["name"] != document_current["name"].strip():
            print("  Warning: Value Name Not Trimmed")

        # assert document_current["name"] == document_current["name"].strip()


def _validate_patient_collection_activity(
    *,
    collection: DocumentSet,
):
    """
    Validate additional properties of activity documents.
    """

    activity_documents = collection.filter_match(
        match_type="activity",
    )
    value_documents = collection.filter_match(
        match_type="value",
    )

    for document_current in activity_documents.filter_match(
        match_deleted=False,
    ):
        # If the activity has a value, the referenced value must exist.
        if "valueId" in document_current:
            assert value_documents.filter_match(
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_current),
                match_values={"valueId": document_current["valueId"]},
            ).is_unique()

        # For the time that each activity exists, its name must be unique.
        assert activity_documents.filter_match(
            match_datetime_at=datetime_from_document(document=document_current),
            match_deleted=False,
            match_values={
                "name": document_current["name"],
            },
        ).is_unique()


def _validate_patient_collection_activity_logs(
    *,
    collection: DocumentSet,
):
    """
    Validate additional properties of activity log documents.
    """

    scheduled_activity_documents = collection.filter_match(
        match_type="scheduledActivity",
    )

    for document_current in collection.filter_match(
        match_type="activityLog",
        match_deleted=False,
    ):
        # The referenced scheduledActivity must exist.
        # The snapshot of the scheduledActivity must match.
        scheduled_activity_current = scheduled_activity_documents.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=document_current),
            match_values={
                "scheduledActivityId": document_current["scheduledActivityId"]
            },
        ).unique()
        assert (
            document_current["dataSnapshot"]["scheduledActivity"]
            == scheduled_activity_current
        )


def _validate_patient_collection_activity_schedules(
    *,
    collection: DocumentSet,
):
    """
    Validate additional properties of activity schedule documents.
    """

    activity_documents = collection.filter_match(
        match_type="activity",
    )
    activity_schedule_documents = collection.filter_match(
        match_type="activitySchedule",
    )
    scheduled_activity_documents = collection.filter_match(
        match_type="scheduledActivity"
    )

    for document_current in activity_schedule_documents.filter_match(
        match_deleted=False,
    ):
        # The referenced activity must exist at the time of the activity schedule.
        assert activity_documents.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=document_current),
            match_values={"activityId": document_current["activityId"]},
        ).is_unique()

    # All revisions of an activity schedule must reference the same activity.
    for (document_key, document_revisions) in (
        activity_schedule_documents.filter_match(
            match_deleted=False,
        )
        .group_revisions()
        .items()
    ):
        activity_id = None
        for (index_current, revision_current) in enumerate(document_revisions):
            if index_current == 0:
                activity_id = revision_current["activityId"]
            else:
                assert revision_current["activityId"] == activity_id

    # Every activity schedule must result in at least one scheduled activity
    for activity_schedule_current in activity_schedule_documents.filter_match(
        match_deleted=False,
        match_values={
            "_rev": 1,
        },
    ):
        assert not scheduled_activity_documents.filter_match(
            match_deleted=False,
            match_values={
                "activityScheduleId": activity_schedule_current["activityScheduleId"]
            },
        ).is_empty()


def _validate_patient_collection_scheduled_activities(
    *,
    collection: DocumentSet,
):
    """
    Validate additional properties of scheduled activity documents.
    """

    activity_documents = collection.filter_match(
        match_type="activity",
    )
    activity_schedule_documents = collection.filter_match(
        match_type="activitySchedule",
    )
    scheduled_activity_documents = collection.filter_match(
        match_type="scheduledActivity",
    )
    value_documents = collection.filter_match(
        match_type="value",
    )

    # Each scheduled activity must have been initially created immediately after its activity schedule
    for scheduled_activity_current in scheduled_activity_documents.filter_match(
        match_deleted=False,
        match_values={"_rev": 1},
    ):
        activity_schedule_current = activity_schedule_documents.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(
                document=scheduled_activity_current
            ),
            match_values={
                "activityScheduleId": scheduled_activity_current["activityScheduleId"]
            },
        ).unique()

        datetime_scheduled_activity = datetime_from_document(
            document=scheduled_activity_current
        )
        datetime_activity_schedule = datetime_from_document(
            document=activity_schedule_current
        )
        timedelta_difference = (
            datetime_scheduled_activity - datetime_activity_schedule
        ).total_seconds()

        # This is incredibly slow, most of these are 0 or 1.
        # Only took this long when running locally against dev, due to database latency.
        assert timedelta_difference < 60

    # Within revisions of a scheduled activity, some fields are not allowed to change.
    for (
        scheduled_activity_current_revisions
    ) in scheduled_activity_documents.group_revisions().values():
        scheduled_activity_current_revisions = (
            scheduled_activity_current_revisions.order_by_revision()
        )

        revision_previous = None
        for revision_current in scheduled_activity_current_revisions:
            if not revision_current.get("_deleted", False) and revision_previous:
                # The due date cannot change
                assert revision_current["dueDate"] == revision_previous["dueDate"]

            revision_previous = revision_current

    for scheduled_activity_current in scheduled_activity_documents.filter_match(
        match_deleted=False,
    ):
        # A referenced activity schedule might no longer exist.
        # This is because we do not update scheduled activities in the past.
        # A referenced activity schedule must have existed at some point.
        # Its snapshot must be current or what it was before deletion.
        activity_schedule_snapshot = activity_schedule_documents.filter_match(
            match_datetime_at=datetime_from_document(
                document=scheduled_activity_current
            ),
            match_values={"_set_id": scheduled_activity_current["activityScheduleId"]},
        ).unique()
        if activity_schedule_snapshot.get("_deleted"):
            # Snapshot should be of the state immediately before deletion.
            assert activity_schedule_snapshot["_deleted"]

            activity_schedule_snapshot = activity_schedule_documents.filter_match(
                match_deleted=False,
                match_values={
                    "_rev": activity_schedule_snapshot["_rev"] - 1,
                    "activityScheduleId": scheduled_activity_current[
                        "activityScheduleId"
                    ],
                },
            ).unique()

        assert (
            scheduled_activity_current["dataSnapshot"]["activitySchedule"]
            == activity_schedule_snapshot
        )

        # The referenced activity must exist.
        # The snapshot of the activity must match.
        activity_snapshot = activity_documents.filter_match(
            match_datetime_at=datetime_from_document(
                document=scheduled_activity_current
            ),
            match_values={"_set_id": activity_schedule_snapshot["activityId"]},
        ).unique()
        if activity_snapshot.get("_deleted"):
            # Snapshot should be of the state immediately before deletion.
            assert activity_snapshot["_deleted"]

            activity_snapshot = activity_documents.filter_match(
                match_deleted=False,
                match_values={
                    "_rev": activity_snapshot["_rev"] - 1,
                    "activityId": activity_schedule_snapshot["activityId"],
                },
            ).unique()

        assert (
            scheduled_activity_current["dataSnapshot"]["activity"] == activity_snapshot
        )

        # If the activity has a value, the referenced value must exist.
        # If the activity has a value, the snapshot of the activity must match.
        if "valueId" in activity_snapshot:
            value_snapshot = value_documents.filter_match(
                match_datetime_at=datetime_from_document(
                    document=scheduled_activity_current
                ),
                match_values={
                    "_set_id": activity_snapshot["valueId"],
                },
            ).unique()
            if value_snapshot.get("_deleted"):
                # Snapshot should be of the state immediately before deletion.
                assert value_snapshot["_deleted"]

                value_snapshot = value_documents.filter_match(
                    match_deleted=False,
                    match_values={
                        "_rev": value_snapshot["_rev"] - 1,
                        "valueId": activity_snapshot["valueId"],
                    },
                ).unique()

            assert scheduled_activity_current["dataSnapshot"]["value"] == value_snapshot
        else:
            # There must not be a value snapshot
            assert "value" not in scheduled_activity_current["dataSnapshot"]


def _validate_patient_collection_values(
    *,
    collection: DocumentSet,
):
    """
    Validate additional properties of value documents.
    """

    value_documents = collection.filter_match(
        match_type="value",
    )

    for document_current in value_documents.filter_match(
        match_deleted=False,
    ):
        # For the time that each value exists, its name/lifeArea tuple must be unique.
        assert value_documents.filter_match(
            match_datetime_at=datetime_from_document(document=document_current),
            match_deleted=False,
            match_values={
                "name": document_current["name"],
                "lifeAreaId": document_current["lifeAreaId"],
            },
        ).is_unique()
