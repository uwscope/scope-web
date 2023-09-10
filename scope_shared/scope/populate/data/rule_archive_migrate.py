import copy
from pathlib import Path
from typing import List, Optional

import scope.populate.data.archive
import scope.populate.data.migrations.migration_v0_5_0
import scope.populate.data.migrations.migration_v0_7_0
import scope.populate.data.migrations.migration_v0_9_0
import scope.populate.data.validate
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
        dry_run = action.get("dry_run", False)

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
            dry_run=dry_run,
        )

        return populate_config


def _archive_migrate(
    *,
    archive_path: Path,
    password: str,
    archive_destination_path: Path,
    migration: str,
    dry_run: bool,
):
    # Obtain the archive
    archive = scope.populate.data.archive.Archive.read_archive(
        archive_path=archive_path,
        password=password,
    )

    if migration == "v0.5.0":
        archive = (
            scope.populate.data.migrations.migration_v0_5_0.archive_migrate_v0_5_0(
                archive=archive,
            )
        )
    elif migration == "v0.7.0":
        archive = (
            scope.populate.data.migrations.migration_v0_7_0.archive_migrate_v0_7_0(
                archive=archive,
                archive_path=archive_path,
            )
        )
    elif migration == "v0.9.0":
        archive = (
            scope.populate.data.migrations.migration_v0_9_0.archive_migrate_v0_9_0(
                archive=archive,
            )
        )
    else:
        raise ValueError("No migration performed")

    # Validate the migrated archive
    scope.populate.data.validate.validate_archive(archive=archive)

    # If this is a dry run, stop before doing the export
    assert not dry_run

    # Export the migrated archive
    scope.populate.data.archive.Archive.write_archive(
        archive=archive,
        archive_path=archive_destination_path,
        password=password,
    )
