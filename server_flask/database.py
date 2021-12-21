# https://flask.palletsprojects.com/en/0.12.x/appcontext/
import logging
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
