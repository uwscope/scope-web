# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

from scope.documents.document_set import datetime_from_document, DocumentSet
import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def validate_archive(*, archive: scope.populate.data.archive.Archive,):
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


def _validate_archive_document_schema(*, archive: scope.populate.data.archive.Archive,):
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
        if document_current["_type"] == "activityLog":
            assert "scheduledActivity" in document_current["dataSnapshot"]


def _validate_archive_expected_collections(*, archive: scope.populate.data.archive.Archive,):
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


def _validate_patient_collection(*, collection: DocumentSet,):
    """
    Validate the entire set of documents in a patient collection.
    """

    _validate_patient_collection_documents(collection=collection)

    _validate_patient_collection_activity_logs(collection=collection)
    _validate_patient_collection_scheduled_activities(collection=collection)


def _validate_patient_collection_documents(*, collection: DocumentSet,):
    """
    Validate the core properties of documents.
    """

    # Every document must have a unique id
    existing_document_ids = []
    for document_current in collection:
        assert document_current["_id"] not in existing_document_ids
        existing_document_ids.append(document_current["_id"])

    # Every document key must be unique,
    # with incrementing revisions,
    # with monotonically increasing times
    for revisions_current in collection.group_revisions().values():
        document_previous = None
        for index, document_current in enumerate(revisions_current.order_by_revisions()):
            assert document_current["_rev"] == index + 1

            if document_previous:
                assert datetime_from_document(document=document_current) >= datetime_from_document(document=document_previous)

            document_previous = document_current


def _validate_patient_collection_activity_logs(*, collection: DocumentSet,):
    """
    Validate additional properties of activity log documents.
    """

    scheduled_activity_documents = collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    )

    for document_current in collection.filter_match(
        match_type="activityLog",
        match_deleted=False,
    ):
        # The snapshot of the scheduledActivity must match
        scheduled_activity_current = scheduled_activity_documents.filter_match(
            match_datetime_at=datetime_from_document(document=document_current),
            match_values={
                "scheduledActivityId": document_current["scheduledActivityId"]
            }
        ).unique()
        assert document_current["dataSnapshot"]["scheduledActivity"] == scheduled_activity_current


def _validate_patient_collection_scheduled_activities(*, collection: DocumentSet,):
    """
    Validate additional properties of scheduled activity documents.
    """

    activity_documents = collection.filter_match(
        match_type="activity",
        match_deleted=False,
    )
    activity_schedule_documents = collection.filter_match(
        match_type="activitySchedule",
        match_deleted=False,
    )
    value_documents = collection.filter_match(
        match_type="value",
        match_deleted=False,
    )

    for document_current in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        # The snapshot of the activitySchedule must match
        activity_schedule_current = activity_schedule_documents.filter_match(
            match_datetime_at=datetime_from_document(document=document_current),
            match_values={
                "activityScheduleId": document_current["activityScheduleId"]
            }
        ).unique()
        assert document_current["dataSnapshot"]["activitySchedule"] == activity_schedule_current

        # The snapshot of the activity must match
        activity_current = activity_documents.filter_match(
            match_datetime_at=datetime_from_document(document=document_current),
            match_values={
                "activityId": activity_schedule_current["activityId"]
            }
        ).unique()
        assert document_current["dataSnapshot"]["activity"] == activity_current

        # If the activity has a value, the snapshot of the activity must match
        if "valueId" in activity_current:
            value_current = value_documents.filter_match(
                match_datetime_at=datetime_from_document(document=document_current),
                match_values={
                    "valueId": activity_current["valueId"]
                }
            ).unique()
            assert document_current["dataSnapshot"]["value"] == value_current
