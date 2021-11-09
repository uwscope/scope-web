import os

from flask import current_app
from pymongo import MongoClient


class DocumentDB(object):
    """
    Configuration for connection to a DocumentDB instance.
    """

    # _db_user: str
    # _db_password: str
    # _database: str
    # DATABASE: None

    """
    def __init__(self, *, db_user: str, db_password: str, database: str):
        self._db_user = db_user
        self._db_password = db_password
        self._database = database
    """

    @staticmethod
    def initialize():
        # Connect to DocumentDB

        db_user = current_app.config["DB_USER"]
        db_password = current_app.config["DB_PASSWORD"]
        database = current_app.config["DATABASE"]

        client = MongoClient(
            host=["localhost"],
            port=int(os.getenv("LOCAL_DOCUMENTDB_PORT")),
            connect=True,
            username=db_user,
            password=db_password,
            tls=True,
            tlsInsecure=True,
        )
        DocumentDB.DB = client[database]

    """
    @property
    def db_password(self) -> str:
        return self._db_password

    @property
    def db_user(self) -> str:
        return self._db_user

    @property
    def database(self) -> str:
        return self._database
    """

    @staticmethod
    def insert(collection, data):
        DocumentDB.DB[collection].insert(data)

    @staticmethod
    def find_one(collection, query):
        return DocumentDB.DB[collection].find_one(query)
