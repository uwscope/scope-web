import json
from pathlib import Path
import pymongo.database
from typing import List, Optional
import zipfile

import scope.database.document_utils as document_utils
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "export_database"


class ExportDatabase(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current.get("action", None) == ACTION_NAME:
                return _ExportDatabaseAction()

        return None


class _ExportDatabaseAction(PopulateAction):
    def prompt(self) -> List[str]:
        return ["Export database"]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Retrieve and remove our action
        for action_current in populate_config["actions"]:
            if action_current.get("action", None) == ACTION_NAME:
                populate_config["actions"].remove(action_current)
                break

        # Perform the export
        _export_database(
            database=populate_context.database,
        )

        return populate_config


def _export_database(
    *,
    database: pymongo.database.Database,
):
    # The export is stored in a single zip file
    with zipfile.ZipFile(
        "export.zip",
        mode="x",
        compression=zipfile.ZIP_LZMA,
    ) as zipfile_export:
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
                    str(Path(collection_name_current, "{}.json".format(document_current["_id"]))),
                    data=document_bytes,
                )
