from typing import List, Optional

import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results


def get_clinical_history(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[dict]:
    """
    Retrieve "clinicalHistory" document.
    """
    collection = database.get_collection(name=collection_name)

    query = {
        "type": "clinicalHistory",
    }

    # Find the document with highest `v`.
    clinical_history = collection.find_one(
        filter=query, sort=[("_rev", pymongo.DESCENDING)]
    )

    if "_id" in clinical_history:
        clinical_history["_id"] = str(clinical_history["_id"])
    # TODO: Verify schema against safety-plan json.

    return clinical_history


def create_clinical_history(
    *, database: pymongo.database.Database, collection_name: str, clinical_history: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the "valuesInventory" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=clinical_history)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
