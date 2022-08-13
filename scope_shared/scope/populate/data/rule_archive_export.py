from pathlib import Path
import pymongo.database
from typing import Dict, List, Optional

import scope.populate.data.archive
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "archive_export"


class ArchiveExport(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ArchiveExportAction(
                archive=action_current["archive"],
            )

        return None


class _ArchiveExportAction(PopulateAction):
    archive: str

    def __init__(
        self,
        *,
        archive: str,
    ):
        self.archive = archive

    def prompt(self) -> List[str]:
        return ["Export archive: {}".format(self.archive)]

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

        # Ensure archive does not already exist
        if Path(self.archive).exists():
            raise ValueError("Archive already exists")

        # Prompt for a password
        password = input("Enter archive password: ")
        password_confirm = input("Confirm archive password: ")
        if password != password_confirm:
            raise ValueError("Password mismatch.")

        # Perform the export
        _archive_export(
            database=populate_context.database,
            archive_path=Path(self.archive),
            password=password,
        )

        return populate_config


def _archive_export(
    *,
    database: pymongo.database.Database,
    archive_path: Path,
    password: str,
):
    entries: Dict[Path, dict] = {}

    # Each collection is stored as a directory
    collection_names = database.list_collection_names()
    for collection_name_current in collection_names:
        collection_current = database[collection_name_current]

        # Each document is stored as a file in that directory
        for document_current in collection_current.find():
            entries[
                Path(
                    collection_name_current,
                    "{}.json".format(document_current["_id"]),
                )
            ] = document_current

    # Store the collection of entries to an archive
    scope.populate.data.archive.Archive.write_archive(
        archive=scope.populate.data.archive.Archive(entries=entries),
        archive_path=archive_path,
        password=password,
    )
