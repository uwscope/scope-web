# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
from pathlib import Path
from typing import Dict

import scope.populate.data.archive


def archive_migrate_v0_5_0(
    *,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
    #
    # Migration for schema modifications in #335
    # https://github.com/uwscope/scope-web/pull/335
    #
    migrated_entries: Dict[Path, dict] = {}
    for (path_current, document_current) in archive.entries.items():
        path_current = copy.deepcopy(path_current)
        document_current = copy.deepcopy(document_current)

        # #335 migration applies to activityLog documents
        if document_current["_type"] == "activityLog":
            # If "success" is "No", remove any "accomplishment" or "pleasure"
            if document_current["success"] == "No":
                if "accomplishment" in document_current:
                    del document_current["accomplishment"]
                if "pleasure" in document_current:
                    del document_current["pleasure"]

        migrated_entries[path_current] = document_current

    return scope.populate.data.archive.Archive(entries=migrated_entries)
