from typing import Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "clinicalHistory"


def get_clinical_history(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def put_clinical_history(
    *,
    collection: pymongo.collection.Collection,
    clinical_history: dict,
) -> scope.database.collection_utils.PutResult:
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=clinical_history,
    )
