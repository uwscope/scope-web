import hashlib
import re
from typing import List, Optional

import bson
import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results

DOCUMENT_TYPE = "session"


def get_sessions(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[list]:
    """
    Retrieve list of "session" document.
    """

    collection = database.get_collection(name=collection_name)

    # Find unique session ids and then get document with latest _rev from them.
    pipeline = [
        {"$match": {"_type": "session"}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "$_session_id",
                "latest_session_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_session_document"}},
    ]

    found_sessions = list(collection.aggregate(pipeline))
    if found_sessions is not None:
        for found_session in found_sessions:
            if "_id" in found_session:
                found_session["_id"] = str(found_session["_id"])

    return found_sessions


def get_session(
    *, database: pymongo.database.Database, collection_name: str, session_id: str
) -> Optional[list]:
    """
    Retrieve "session" document.
    """

    collection = database.get_collection(name=collection_name)

    query = {"_type": "session", "_session_id": session_id}

    # Find the document with highest `_rev`.
    session = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])

    if "_id" in session:
        session["_id"] = str(session["_id"])
    # TODO: Verify schema against session json.

    return session


def create_session(
    *, database: pymongo.database.Database, collection_name: str, session: dict
):
    """
    Create the "session" document.
    """

    collection = database.get_collection(name=collection_name)

    # Make sure _session_id does not already exist.
    query = {"_type": "session", "_session_id": session["_session_id"]}
    if collection.find_one(filter=query) is None:
        try:
            result = collection.insert_one(document=session)
            return result
        except pymongo.errors.DuplicateKeyError:
            return None
    else:
        return None


def update_session(
    *, database: pymongo.database.Database, collection_name: str, session: dict
):
    """
    Update (insert) the "session" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=session)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
