import copy
from pathlib import Path
from typing import Dict, List, Optional

import scope.populate.data.archive
import scope.schema
import scope.schema_utils
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "archive_migrate"


class ArchiveMigrate(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ArchiveMigrateAction(
                archive=action_current["archive"],
            )

        return None


class _ArchiveMigrateAction(PopulateAction):
    archive: str

    def __init__(
        self,
        *,
        archive: str,
    ):
        self.archive = archive

    def prompt(self) -> List[str]:
        return ["Migrate archive: {}".format(self.archive)]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Retrieve and remove our action
        action = None
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue
            if action_current["archive"] != self.archive:
                continue

            action = action_current
            break

        # Confirm we found the action
        if not action:
            raise ValueError("populate_config was modified")

        # Remove the action from the pending list
        populate_config["actions"].remove(action)

        # Obtain expected variables from action
        archive_destination = action["archive_destination"]
        migration = action["migration"]

        # Ensure archive exists
        if not Path(self.archive).exists():
            raise ValueError("Archive does not exist")
        # Ensure destination archive does not already exist
        if Path(archive_destination).exists():
            raise ValueError("Destination archive already exists")

        # Prompt for a password
        password = input("Enter archive password: ")

        # Perform the export
        _archive_migrate(
            archive_path=Path(self.archive),
            password=password,
            archive_destination_path=Path(archive_destination),
            migration=migration,
        )

        return populate_config


def _archive_migrate(
    *,
    archive_path: Path,
    password: str,
    archive_destination_path: Path,
    migration: str,
):
    # Obtain all entries in the archive
    archive = scope.populate.data.archive.Archive.read_archive(
        archive_path=archive_path,
        password=password,
    )
    entries: Dict[Path, dict] = archive.entries

    # First simple migration, structure can be added for later migrations
    if migration == "v0.5.0":
        #
        # Migration for schema enhancements in #335
        # https://github.com/uwscope/scope-web/pull/335
        #
        migrated_entries: Dict[Path, dict] = {}
        for (path_current, document_current) in entries.items():
            path_current = copy.deepcopy(path_current)
            document_current = copy.deepcopy(document_current)

            # Migration applies only to activityLog documents
            if document_current["_type"] == "activityLog":
                # If "success" is "No", remove any "accomplishment" or "pleasure"
                if document_current["success"] == "No":
                    if "accomplishment" in document_current:
                        del document_current["accomplishment"]
                    if "pleasure" in document_current:
                        del document_current["pleasure"]

            migrated_entries[path_current] = document_current

        entries = migrated_entries
    else:
        raise ValueError("No migration performed")

    # Export the migrated entries
    # Store the collection of entries to an archive
    scope.populate.data.archive.Archive.write_archive(
        archive=scope.populate.data.archive.Archive(entries=entries),
        archive_path=archive_destination_path,
        password=password,
    )
