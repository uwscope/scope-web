from typing import List, Optional

import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results


def get_values(
    *, database: pymongo.database.Database, collection: str
) -> Optional[dict]:
    """
    Retrieve "valuesInventory" document.
    """
    collection = database.get_collection(name=collection)

    query = {
        "type": "valuesInventory",
    }

    # Find the document with highest `v`.
    values_inventory = collection.find_one(
        filter=query, sort=[("_rev", pymongo.DESCENDING)]
    )

    # TODO: Verify schema against values-inventory json.

    return values_inventory


def create_values(
    *, database: pymongo.database.Database, collection: str, values_inventory: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the "valuesInventory" document.
    """

    collection = database.get_collection(name=collection)

    try:
        result = collection.insert_one(document=values_inventory)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
