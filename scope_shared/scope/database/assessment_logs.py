import hashlib
import re
from typing import List, Optional

import bson
import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results

TYPE = "assessmentLog"


def get_assessment_logs(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[list]:
    """
    Retrieve list of "assessmentLog" document.
    """

    collection = database.get_collection(name=collection_name)

    # NOTE: James.
    # Find unique log ids and assessment names and then get document with latest _rev from them.
    pipeline = [
        {"$match": {"_type": TYPE}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": {
                    "_log_id": "$_log_id",
                    "assessmentName": "$assessmentName",
                },
                "latest_assessment_log_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_assessment_log_document"}},
    ]

    found_assessment_logs = list(collection.aggregate(pipeline))
    if found_assessment_logs is not None:
        for fal in found_assessment_logs:
            if "_id" in fal:
                fal["_id"] = str(fal["_id"])

    return found_assessment_logs


def get_assessment_log(
    *, database: pymongo.database.Database, collection_name: str, log_id: str
) -> Optional[list]:
    """
    Retrieve "assessmentLog" document.
    """

    collection = database.get_collection(name=collection_name)

    # NOTE: This is wrong. There are multiple assessment log documents because uniquness is on (log_id, assessmentName).
    query = {"_type": TYPE, "_log_id": log_id}

    # Find the document with highest `_rev`.
    assessment_log = collection.find_one(
        filter=query, sort=[("_rev", pymongo.DESCENDING)]
    )

    if "_id" in assessment_log:
        assessment_log["_id"] = str(assessment_log["_id"])
    # TODO: Verify schema against assessment log json.

    return assessment_log


def create_assessment_log(
    *, database: pymongo.database.Database, collection_name: str, assessment_log: dict
):
    """
    Create the "assessmentLog" document.
    """

    collection = database.get_collection(name=collection_name)

    # Make sure _log_id does not already exist. NOTE: needs to have assessmentName as well.
    query = {"_type": TYPE, "_log_id": assessment_log["_log_id"]}
    if collection.find_one(filter=query) is None:
        try:
            result = collection.insert_one(document=assessment_log)
            return result
        except pymongo.errors.DuplicateKeyError:
            return None
    else:
        return None


def update_assessment_log(
    *, database: pymongo.database.Database, collection_name: str, assessment_log: dict
):
    """
    Update (insert) the "assessmentLog" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=assessment_log)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
