import json
from pathlib import Path
from typing import List, Optional

import scope.populate.data.archive
import scope.schema
import scope.schema_utils
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "archive_validate"


class ArchiveValidate(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ArchiveValidateAction(
                archive=action_current["archive"],
            )

        return None


class _ArchiveValidateAction(PopulateAction):
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
        populate_config["actions"].remove(action)

        # Ensure archive exists
        if not Path(self.archive).exists():
            raise ValueError("Archive does not exist")

        # Prompt for a password
        password = input("Enter archive password: ")

        # Perform the export
        _archive_validate(
            archive_path=Path(self.archive),
            password=password,
        )

        return populate_config


def _archive_validate(
    *,
    archive_path: Path,
    password: str,
):
    archive = scope.populate.data.archive.Archive.read_archive(
        archive_path=archive_path,
        password=password,
    )

    # Validate every document matches the document schema
    for document_current in archive.entries.values():
        # Assert the document schema
        scope.schema_utils.assert_schema(
            data=document_current,
            schema=scope.schema.document_schema,
        )

        # TODO: A more complete validation, shared with rule_archive_restore
