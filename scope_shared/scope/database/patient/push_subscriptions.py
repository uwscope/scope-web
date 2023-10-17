from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "pushSubscription"
SEMANTIC_SET_ID = "pushSubscriptionId"


def get_push_subscriptions(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "pushSubscription" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_push_subscription(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "pushSubscription" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_push_subscription(
    *,
    collection: pymongo.collection.Collection,
    push_subscription: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "pushSubscription" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=push_subscription,
    )


def put_push_subscription(
    *,
    collection: pymongo.collection.Collection,
    push_subscription: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "pushSubscription" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=push_subscription,
    )
