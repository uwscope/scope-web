# https://flask.palletsprojects.com/en/0.12.x/appcontext/
import os
from datetime import datetime

from bson import ObjectId
from flask import current_app, g
from pymongo import MongoClient


def get_db():
    """
    Returns instance of `pymongo.database.Database`
    https://pymongo.readthedocs.io/en/stable/api/pymongo/database.html?highlight=Database#pymongo.database.Database
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = MongoClient(
            connect=True,
            host=current_app.config["DOCUMENTDB_HOST"],
            port=current_app.config["DOCUMENTDB_PORT"],
            directConnection=current_app.config["DOCUMENTDB_DIRECTCONNECTION"],
            tls=True,
            tlsInsecure=current_app.config["DOCUMENTDB_TLSINSECURE"],
            username=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
        )[current_app.config["DATABASE_NAME"]]
    return db


def insert(document, db, collection):
    document["created_at"] = datetime.utcnow()
    inserted = db[collection].insert_one(document)
    return str(inserted.inserted_id)


def find(query, db, collection):
    found = db[collection].find(filter=query)
    found = list(found)
    # To serialize object, convert _id in document to string.
    for doc in found:
        doc.update((k, str(v)) for k, v in doc.items() if k == "_id")

    return found


def find_by_id(id, db, collection):
    # TODO: Check if 'id' is a valid ObjectId, it must be a 12-byte input or a 24-character hex string.
    found = db[collection].find_one({"_id": ObjectId(id)})

    if "_id" in found:
        found["_id"] = str(found["_id"])

    return found
