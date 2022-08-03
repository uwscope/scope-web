import json
from pathlib import Path
import pymongo.database
import pyzipper
from typing import List, Optional

import scope.database.document_utils as document_utils
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
    # Ensure archive directory exists
    if archive_path.parent:
        archive_path.parent.mkdir(parents=True, exist_ok=True)

    # The export is stored in a single zip file
    with pyzipper.AESZipFile(
        archive_path,
        mode="x",
        compression=pyzipper.ZIP_LZMA,
        encryption=pyzipper.WZ_AES,
    ) as zipfile_export:
        # Set the password
        zipfile_export.setpassword(password.encode("utf-8"))

        # Each collection is stored as a directory
        collection_names = database.list_collection_names()
        for collection_name_current in collection_names:
            collection_current = database[collection_name_current]

            # Each document is stored as a file
            for document_current in collection_current.find():
                document_current = document_utils.normalize_document(
                    document=document_current
                )
                document_string = json.dumps(
                    document_current,
                    indent=2,
                )
                document_bytes = document_string.encode("utf-8")

                zipfile_export.writestr(
                    str(
                        Path(
                            collection_name_current,
                            "{}.json".format(document_current["_id"]),
                        )
                    ),
                    data=document_bytes,
                )