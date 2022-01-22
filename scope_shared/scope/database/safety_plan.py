from typing import List, Optional

import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results


def get_safety_plan(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[dict]:
    """
    Retrieve "safetyPlan" document.
    """
    collection = database.get_collection(name=collection_name)

    query = {
        "_type": "safetyPlan",
    }

    # Find the document with highest `v`.
    safety_plan = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])

    if "_id" in safety_plan:
        safety_plan["_id"] = str(safety_plan["_id"])
    # TODO: Verify schema against safety-plan json.

    return safety_plan


def create_safety_plan(
    *, database: pymongo.database.Database, collection_name: str, safety_plan: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the "valuesInventory" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=safety_plan)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
