# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
import pprint
from pathlib import Path
from scope.documents.document_set import DocumentSet
import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def archive_migrate_v0_7_0(
    *,
    archive_path: Path,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
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

        print("Deleted {} collections containing a total of {} documents.".format(
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


        archive.replace_collection_documents(
            collection=patients_document_current["collection"],
            document_set=patient_collection,
        )

    return archive


def _migrate_assessment_log_with_embedded_assessment(
    collection: DocumentSet,
) -> DocumentSet:
    """
    These resulted from some development / experimentation.
    """

    original_documents = collection.filter_match(
        match_type="assessmentLog"
    )

    migrated_documents = []
    for document_current in original_documents:
        document_current = copy.deepcopy(document_current)

        if "assessment" in document_current:
            document_current["assessmentId"] = document_current["assessment"]["assessmentId"]
            del document_current["assessment"]

        scope.schema_utils.assert_schema(
            data=document_current,
            schema=scope.schema.assessment_log_schema,
        )

        migrated_documents.append(document_current)

    return collection.remove_all(
        documents=original_documents,
    ).union(
        documents=migrated_documents
    )
    migrated_documents = []

    for document_current in collection:
        document_current = copy.deepcopy(document_current)



        migrated_documents.append(document_current)

    return DocumentSet(documents=migrated_documents)

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
