import json
from pathlib import Path
import pymongo.database
import pyzipper
from typing import List, Optional

import scope.database.document_utils as document_utils
import scope.schema
import scope.schema_utils
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "validate_archive"


class ValidateArchive(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ValidateArchiveAction(
                archive=action_current["archive"]
            )

        return None


class _ValidateArchiveAction(PopulateAction):
    archive: str

    def __init__(
        self,
        *,
        archive: str,
    ):
        self.archive = archive

    def prompt(self) -> List[str]:
        return ["Validate archive: {}".format(self.archive)]

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
        # populate_config["actions"].remove(action)

        # Prompt for a password
        password = input("Enter archive password: ")

        # Ensure archive exists
        if not Path(self.archive).exists():
            raise ValueError("Archive does not exist")

        # Perform the export
        _validate_archive(
            archive=Path(self.archive),
            password=password,
        )

        return populate_config


def _validate_archive(
    *,
    archive: Path,
    password: str,
):
    # The export is stored in a single zip file
    with pyzipper.AESZipFile(
        archive,
        mode="r",
        compression=pyzipper.ZIP_LZMA,
        encryption=pyzipper.WZ_AES,
    ) as zipfile_validate:
        # Set the password
        zipfile_validate.setpassword(password.encode("utf-8"))

        # Test the archive
        if zipfile_validate.testzip():
            raise ValueError("Invalid archive or password")

        # Each file is a document, validate each document
        for info_current in zipfile_validate.infolist():
            document_bytes = zipfile_validate.read(info_current)
            document_string = document_bytes.decode("utf-8")
            document_current = json.loads(document_string)

            # Assert the document schema
            scope.schema_utils.assert_schema(
                data=document_current,
                schema=scope.schema.document_schema,
            )
