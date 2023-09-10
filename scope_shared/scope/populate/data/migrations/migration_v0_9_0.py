# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
from pathlib import Path
from typing import Dict

import scope.populate.data.archive


def archive_migrate_v0_9_0(
    *,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
    migrated_entries: Dict[Path, dict] = {}
    for (path_current, document_current) in archive.entries.items():
        path_current = copy.deepcopy(path_current)
        document_current = copy.deepcopy(document_current)

        # #442 requires deleting a duplicate providerIdentity
        # https://github.com/uwscope/scope-web/issues/442
        if document_current["_type"] == "providerIdentity":
            if document_current["_id"] not in ["630cd4c8206101c1ff018987"]:
                migrated_entries[path_current] = document_current
        else:
            migrated_entries[path_current] = document_current

    return scope.populate.data.archive.Archive(entries=migrated_entries)
