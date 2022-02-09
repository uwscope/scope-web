from typing import Optional

import pymongo
import pymongo.results
import scope.database.collection_utils

DOCUMENT_TYPE = "patientProfile"


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
    collection: pymongo.collection.Collection,
    patient_profile: dict,
) -> scope.database.collection_utils.PutResult:
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=patient_profile,
    )
