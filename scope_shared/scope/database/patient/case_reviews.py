import hashlib
import re
from typing import List, Optional

import bson
import pymongo
import pymongo.database
import pymongo.errors
import pymongo.results

DOCUMENT_TYPE = "caseReview"


def get_case_reviews(
    *, database: pymongo.database.Database, collection_name: str
) -> Optional[list]:
    """
    Retrieve list of "caseReview" document.
    """

    collection = database.get_collection(name=collection_name)

    # Find unique review ids and then get document with latest _rev from them.
    pipeline = [
        {"$match": {"_type": DOCUMENT_TYPE}},
        {"$sort": {"_rev": pymongo.DESCENDING}},
        {
            "$group": {
                "_id": "$_review_id",
                "latest_case_review_document": {"$first": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$latest_case_review_document"}},
    ]

    found_case_reviews = list(collection.aggregate(pipeline))
    if found_case_reviews is not None:
        for fcr in found_case_reviews:
            if "_id" in fcr:
                fcr["_id"] = str(fcr["_id"])

    return found_case_reviews


def get_case_review(
    *, database: pymongo.database.Database, collection_name: str, review_id: str
) -> Optional[list]:
    """
    Retrieve "caseReview" document.
    """

    collection = database.get_collection(name=collection_name)

    query = {"_type": DOCUMENT_TYPE, "_review_id": review_id}

    # Find the document with highest `_rev`.
    case_review = collection.find_one(filter=query, sort=[("_rev", pymongo.DESCENDING)])

    if "_id" in case_review:
        case_review["_id"] = str(case_review["_id"])
    # TODO: Verify schema against case review json.

    return case_review


def create_case_review(
    *, database: pymongo.database.Database, collection_name: str, case_review: dict
):
    """
    Create the "caseReview" document.
    """

    collection = database.get_collection(name=collection_name)

    # Make sure _review_id does not already exist.
    query = {"_type": DOCUMENT_TYPE, "_review_id": case_review["_review_id"]}
    if collection.find_one(filter=query) is None:
        try:
            result = collection.insert_one(document=case_review)
            return result
        except pymongo.errors.DuplicateKeyError:
            return None
    else:
        return None


def update_case_review(
    *, database: pymongo.database.Database, collection_name: str, case_review: dict
):
    """
    Update (insert) the "caseReview" document.
    """

    collection = database.get_collection(name=collection_name)

    try:
        result = collection.insert_one(document=case_review)
        return result
    except pymongo.errors.DuplicateKeyError:
        return None
