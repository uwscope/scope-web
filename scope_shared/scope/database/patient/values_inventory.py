from typing import Optional

import pymongo.collection
import scope.database.collection_utils
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "valuesInventory"


def get_values_inventory(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def put_values_inventory(
    *,
    collection: pymongo.collection.Collection,
    values_inventory: dict,
) -> scope.database.collection_utils.PutResult:
    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        schema=scope.schema.values_inventory_schema,
        data=values_inventory,
    )

    # Put the document
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=values_inventory,
    )
