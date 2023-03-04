# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

from pathlib import Path
import scope.populate.data.archive


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

        print("Deleted {} documents.".format(len(archive.entries) - len(migrated_entries)))

        archive = scope.populate.data.archive.Archive(entries=migrated_entries)

    #
    # Go through each patient collection
    #
    # for patient_collection_current in archive.

    return archive




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
