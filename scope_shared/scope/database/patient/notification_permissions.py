from typing import Optional

import pymongo.collection
import scope.database.collection_utils
import scope.schema
import scope.schema_utils as schema_utils

DOCUMENT_TYPE = "notificationPermissions"


def get_notification_permissions(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[dict]:
    return scope.database.collection_utils.get_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def put_notification_permissions(
    *,
    collection: pymongo.collection.Collection,
    notification_permissions: dict,
) -> scope.database.collection_utils.PutResult:
    # Enforce the schema
    schema_utils.raise_for_invalid_schema(
        schema=scope.schema.notification_permissions_schema,
        data=notification_permissions,
    )

    # Put the document
    return scope.database.collection_utils.put_singleton(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        document=notification_permissions,
    )
