from typing import List, Optional

import pymongo
import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "session"
DOCUMENT_ID = "sessionId"


def get_sessions(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Retrieve list of "session" document.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_session(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Retrieve "session" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_session(
    *,
    collection: pymongo.collection.Collection,
    session: dict,
) -> scope.database.collection_utils.PutResult:
    """
    Create the "session" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=session[DOCUMENT_ID],
        document=session,
    )


def put_session(
    *,
    collection: pymongo.collection.Collection,
    session: dict,
):
    """
    Update the "session" document.
    """
    # NOTE: Exactly same as post_session, but keeping it here if we need additional computation.

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=session[DOCUMENT_ID],
        document=session,
    )
