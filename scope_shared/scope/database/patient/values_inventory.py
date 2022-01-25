import pymongo
import pymongo.results
from typing import Optional

import scope.database.collection_utils


def get_values_inventory(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type="valuesInventory",
    )


def put_values_inventory(
    *,
    collection: pymongo.collection.Collection,
    values_inventory: dict
) -> scope.database.collection_utils.PutResult:
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type="valuesInventory",
        document=values_inventory,
    )
