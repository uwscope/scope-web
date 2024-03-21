# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
from pathlib import Path
from typing import Dict

import scope.populate.data.archive


def archive_migrate_v0_13_0(
    *,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
    migrated_entries: Dict[Path, dict] = {}
    for (path_current, document_current) in archive.entries.items():
        path_current = copy.deepcopy(path_current)
        document_current = copy.deepcopy(document_current)

        # A handful of fixes are needed
        # due to creation and deletion of duplicate providerIdentity
        if document_current["_id"] in [
            "651b1f005d1f5a97a03ba856",
            "65b1513f591049b47eb7797e",
        ]:
            # These reference an invalid providerId
            assert (
                document_current["primaryCareManager"]["providerId"] == "5tg3mrdhciskg"
            )

            # Replace with the corrected providerId
            document_current["primaryCareManager"]["providerId"] = "lejqulsreik2k"
            migrated_entries[path_current] = document_current
        elif document_current["_id"] == "65f20807a21e04cb343db1b0":
            # Replace with the original provider _id
            path_current = Path("providers", "62412ca1f8528ee296794f57.json")
            document_current["_id"] = "62412ca1f8528ee296794f57"

            migrated_entries[path_current] = document_current
        elif document_current["_id"] == "65f2080ba21e04cb343db1b1":
            # Replace with the original provider _id
            path_current = Path("providers", "62412cacf8528ee296794f61.json")
            document_current["_id"] = "62412cacf8528ee296794f61"

            migrated_entries[path_current] = document_current
        else:
            migrated_entries[path_current] = document_current

    return scope.populate.data.archive.Archive(entries=migrated_entries)
