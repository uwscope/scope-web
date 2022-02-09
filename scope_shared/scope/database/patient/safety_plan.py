from typing import Optional

import pymongo
import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "safetyPlan"


def get_safety_plan(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def put_safety_plan(
    *,
    collection: pymongo.collection.Collection,
    safety_plan: dict,
) -> scope.database.collection_utils.PutResult:
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=safety_plan,
    )
