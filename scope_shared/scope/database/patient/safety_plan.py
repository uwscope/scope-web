from typing import Optional

import pymongo.collection
import scope.database.collection_utils
import scope.schema
import scope.schema_utils as schema_utils

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
    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        schema=scope.schema.safety_plan_schema,
        data=safety_plan,
    )

    # Put the document
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=safety_plan,
    )
