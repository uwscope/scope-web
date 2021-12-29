from typing import List, Optional

import pymongo.database
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

    values_inventory = collection.find_one(filter=query)

    # TODO: Verify schema against values-inventory json.

    return values_inventory
