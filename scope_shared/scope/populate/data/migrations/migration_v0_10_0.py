# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
import pprint

from scope.documents.document_set import DocumentSet

import scope.populate.data.archive


def archive_migrate_v0_10_0(
    *,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
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

        # #416 fixes #428, where value names were not always trimmed
        # https://github.com/uwscope/scope-web/pull/416
        # https://github.com/uwscope/scope-web/issues/428
        patient_collection = _migrate_value_name_trim(
            collection=patient_collection,
        )

        archive.replace_collection_documents(
            collection=patients_document_current["collection"],
            document_set=patient_collection,
        )

    return archive


def _value_snapshots(*, collection: DocumentSet, document_value: dict):
    """
    Obtain all documents that include a snapshot of the provided value document.
    """

    value_snapshot_documents = []

    for document_activity_log in collection.filter_match(
        match_type="activityLog",
        match_deleted=False,
    ):
        if (
            "value"
            in document_activity_log["dataSnapshot"]["scheduledActivity"][
                "dataSnapshot"
            ]
        ):
            if (
                document_activity_log["dataSnapshot"]["scheduledActivity"][
                    "dataSnapshot"
                ]["value"]["_id"]
                == document_value["_id"]
                and document_activity_log["dataSnapshot"]["scheduledActivity"][
                    "dataSnapshot"
                ]["value"]["_rev"]
                == document_value["_rev"]
            ):
                assert (
                    document_activity_log["dataSnapshot"]["scheduledActivity"][
                        "dataSnapshot"
                    ]["value"]
                    == document_value
                )

                value_snapshot_documents.append(document_activity_log)

    for document_scheduled_activity in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        if "value" in document_scheduled_activity["dataSnapshot"]:
            if (
                document_scheduled_activity["dataSnapshot"]["value"]["_id"]
                == document_value["_id"]
                and document_scheduled_activity["dataSnapshot"]["value"]["_rev"]
                == document_value["_rev"]
            ):
                assert (
                    document_scheduled_activity["dataSnapshot"]["value"]
                    == document_value
                )

                value_snapshot_documents.append(document_scheduled_activity)

    return DocumentSet(documents=value_snapshot_documents)


def _migrate_value_name_trim(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    documents_original_need_removed = []
    documents_modified = []

    for document_value_original in collection.filter_match(
        match_type="value", match_deleted=False
    ):
        if document_value_original["name"] != document_value_original["name"].strip():
            # Modify a copy
            document_value_modified = copy.deepcopy(document_value_original)

            # Strip the value name
            document_value_modified["name"] = document_value_original["name"].strip()

            # Apply the modification
            documents_original_need_removed.append(document_value_original)
            documents_modified.append(document_value_modified)

            # Also must strip value name in any existing snapshots
            for document_snapshot_original in _value_snapshots(
                collection=collection, document_value=document_value_original
            ):
                # Modify a copy
                document_snapshot_modified = copy.deepcopy(document_snapshot_original)

                # Modify the snapshot based on document type
                if document_snapshot_original["_type"] == "activityLog":
                    document_snapshot_modified["dataSnapshot"]["scheduledActivity"][
                        "dataSnapshot"
                    ]["value"]["name"] = document_value_modified["name"]
                elif document_snapshot_original["_type"] == "scheduledActivity":
                    document_snapshot_modified["dataSnapshot"]["value"][
                        "name"
                    ] = document_value_modified["name"]
                else:
                    raise ValueError(document_snapshot_original["_type"])

                # Apply the modification
                documents_original_need_removed.append(document_snapshot_original)
                documents_modified.append(document_snapshot_modified)

    return collection.remove_all(documents=documents_original_need_removed).union(
        documents=documents_modified
    )
