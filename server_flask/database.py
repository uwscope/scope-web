import os
from datetime import datetime

from bson import ObjectId
from flask import current_app
from pymongo import MongoClient


class Database(object):
    """
    Configuration for connection to a DocumentDB instance.
    """

    @staticmethod
    def initialize():
        client = MongoClient(
            host="127.0.0.1",
            port=int(os.getenv("LOCAL_DOCUMENTDB_PORT")),
            connect=True,
            directConnection=True,
            username=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            tls=True,
            tlsInsecure=True,
        )

        Database.db = client[current_app.config["DATABASE"]]

    def insert(document, collection_name):
        document["created_at"] = datetime.utcnow()
        inserted = Database.db[collection_name].insert_one(document)
        return str(inserted.inserted_id)

    def find(query, collection_name):
        found = Database.db[collection_name].find(filter=query)
        found = list(found)
        # To serialize object, convert _id in document to string.
        for doc in found:
            doc.update((k, str(v)) for k, v in doc.items() if k == "_id")

        return found

    def find_by_id(id, collection_name):
        # TODO: Check if 'id' is a valid ObjectId, it must be a 12-byte input or a 24-character hex string.
        found = Database.db[collection_name].find_one({"_id": ObjectId(id)})

        if "_id" in found:
            found["_id"] = str(found["_id"])

        return found
