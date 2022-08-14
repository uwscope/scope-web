import json
from pathlib import Path
import pymongo.database
from typing import List, Optional

import scope.database.patients
import scope.populate.data.archive
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema
import scope.schema_utils

ACTION_NAME = "archive_restore"


class ArchiveRestore(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current["action"] != ACTION_NAME:
                continue

            return _ArchiveRestoreAction(
                archive=action_current["archive"],
            )

        return None


class _ArchiveRestoreAction(PopulateAction):
    archive: str

    def __init__(
        self,
        *,
        archive: str,
    ):
        self.archive = archive

    def prompt(self) -> List[str]:
        return ["Restore archive: {}".format(self.archive)]

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

        # Perform the restore
        _archive_restore(
            database=populate_context.database,
            archive_path=Path(self.archive),
            password=password,
        )

        return populate_config


def _archive_restore(
    *,
    database: pymongo.database.Database,
    archive_path: Path,
    password: str,
):
    archive = scope.populate.data.archive.Archive.read_archive(
        archive_path=archive_path,
        password=password,
    )

    # Validate every document matches the document schema
    # TODO: A more complete validation, shared with rule_archive_validate
    for document_current in archive.entries.values():
        # Assert the document schema
        scope.schema_utils.assert_schema(
            data=document_current,
            schema=scope.schema.document_schema,
        )

    # Providers are simple documents in "providers" collection.
    # Database initialization will ensure "providers" collection exists.
    # But it will have an existing "sentinel" that needs to be deleted.
    # Simply restore the "providers" collection.
    restore_providers_documents = archive.providers_documents(
        ignore_sentinel=False,
        collapsed=False,
    )
    _collection_restore(
        collection=database["providers"],
        restore_documents=restore_providers_documents,
        delete_existing_sentinel=True,
    )

    # Patients each have a document in "patients" and then a dedicated collection.
    # Database initialization will ensure "patients" collection exists.
    # But it will have an existing "sentinel" that needs to be deleted.
    # First restore the "patients" collection.
    # Then restore each patient collection.
    # Restore patients by ensuring each step in patient creation.

    # Restore the "patients" collection
    restore_patients_documents = archive.patients_documents(
        ignore_sentinel=False,
        collapsed=False,
    )
    _collection_restore(
        collection=database["patients"],
        restore_documents=restore_patients_documents,
        delete_existing_sentinel=True,
    )

    # Iterate over each patient, restore its collection and documents
    for patient_current_document in archive.patients_documents(
        ignore_sentinel=True,
        collapsed=True,
    ):
        # Recover fields we need from the patient document
        patient_id = patient_current_document["patientId"]
        patient_collection_name = patient_current_document["collection"]
        patient_name = patient_current_document["name"]
        patient_mrn = patient_current_document["MRN"]

        # Ensure the patient collection
        patient_collection = scope.database.patients.ensure_patient_collection(
            database=database,
            patient_id=patient_id,
        )
        if patient_collection.name != patient_collection_name:
            raise RuntimeError("Patient collection name changed")

        # Restore patient documents, including the sentinel
        restore_patient_current_documents = archive.collection_documents(
            collection=patient_collection_name,
            ignore_sentinel=False,
        )
        _collection_restore(
            collection=patient_collection,
            restore_documents=restore_patient_current_documents,
            delete_existing_sentinel=True,
        )

        # Ensure minimal documents.
        # This will usually do nothing, as the existing documents were already restored.
        scope.database.patients.ensure_patient_documents(
            database=database,
            patient_collection=patient_collection,
            patient_id=patient_id,
            patient_name=patient_name,
            patient_mrn=patient_mrn,
        )

        # Ensure a patient identity documents.
        # This will usually do nothing, as the existing documents were already restored.
        scope.database.patients.ensure_patient_identity(
            database=database,
            patient_collection=patient_collection,
            patient_id=patient_id,
            patient_name=patient_name,
            patient_mrn=patient_mrn,
        )


def _collection_restore(
    *,
    collection: pymongo.collection.Collection,
    restore_documents: List[dict],
    delete_existing_sentinel: bool,
):
    if delete_existing_sentinel:
        result = collection.delete_one(
            filter={
                "_type": "sentinel",
            }
        )
        if result.deleted_count != 1:
            raise RuntimeError(
                "Failed to delete existing sentinel in collection: {}".format(
                    collection.name
                )
            )

    result = collection.insert_many(
        documents=restore_documents,
        ordered=False,
    )
    if not result.acknowledged:
        raise RuntimeError("Failed to restore collection: {}".format(collection.name))
