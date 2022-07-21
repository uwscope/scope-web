import json
from pathlib import Path
import pymongo.database
import pyzipper
from typing import List, Optional

import scope.database.document_utils as document_utils
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "export_archive"


class ExportArchive(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ExportDatabaseAction(
                archive=action_current["archive"]
            )

        return None


class _ExportDatabaseAction(PopulateAction):
    archive: str

    def __init__(
        self,
        *,
        archive: str,
    ):
        self.archive = archive

    def prompt(self) -> List[str]:
        return ["Export archive to {}".format(self.archive)]

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

        # Prompt for a password
        password = input("Enter archive password: ")
        password_confirm = input("Confirm archive password: ")
        if password != password_confirm:
            raise ValueError("Password mismatch.")

        # Perform the export
        _export_database(
            database=populate_context.database,
            archive=Path(action["archive"]),
            password=password,
        )

        return populate_config


def _export_database(
    *,
    database: pymongo.database.Database,
    archive: Path,
    password: str,
):
    # Ensure archive directory exists
    if archive.parent:
        archive.parent.mkdir(parents=True, exist_ok=True)

    # The export is stored in a single zip file
    with pyzipper.AESZipFile(
        archive,
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
                    str(Path(
                        collection_name_current,
                        "{}.json".format(document_current["_id"])
                    )),
                    data=document_bytes,
                )
