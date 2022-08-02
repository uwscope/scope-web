import copy
from typing import Optional

import pymongo.database
import scope.database.collection_utils
import scope.database.patients
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "profile"


def get_patient_profile(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def put_patient_profile(
    *,
    database: pymongo.database.Database,
    collection: pymongo.collection.Collection,
    patient_id: str,
    patient_profile: dict,
) -> scope.database.collection_utils.PutResult:
    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        schema=scope.schema.patient_profile_schema,
        data=patient_profile,
    )

    # Put the document
    result = scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=patient_profile,
    )

    # Determine whether we need to also maintain the patient identity
    if result.inserted_count:
        # If a patient identity already exists,
        # it must be maintained to match the profile.
        # If no patient identity exists yet,
        # (e.g., if this profile is put in the midst of patient creation),
        # then a patient identity will not yet exist to be maintained.
        patient_identity = scope.database.patients.get_patient_identity(
            database=database,
            patient_id=patient_id,
        )

        if patient_identity:
            updated_identity = copy.deepcopy(patient_identity)
            updated_identity["MRN"] = result.document["MRN"]
            updated_identity["name"] = result.document["name"]

            if patient_identity != updated_identity:
                del updated_identity["_id"]

                scope.database.patients.put_patient_identity(
                    database=database,
                    patient_id=patient_id,
                    patient_identity=updated_identity,
                )

    return result
