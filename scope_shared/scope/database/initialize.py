# https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html
# https://pymongo.readthedocs.io/en/stable/tutorial.html
# https://aws.amazon.com/blogs/database/how-to-index-on-amazon-documentdb-with-mongodb-compatibility/


import bson.objectid
import pymongo.database

import scope.database.patients


def initialize(*, database: pymongo.database.Database):
    """
    Initialize a database, bringing it from empty to our expected state (e.g., it will pass all tests).

    Initialization should be idempotent.
    """

    initialize_patients_collection(database=database)


def initialize_patients_collection(*, database: pymongo.database.Database):
    """
    Initialize a patients collection.
    """

    # Get or create a patients collection
    patients_collection = database.get_collection(scope.database.patients.PATIENTS_COLLECTION_NAME)

    # Ensure a sentinel document
    result = patients_collection.find_one(
        filter={
            "type": "sentinel",
        }
    )
    if result is None:
        patients_collection.insert_one(
            {
                "_id": bson.objectid.ObjectId(),
                "type": "sentinel",
            }
        )
