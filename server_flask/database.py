import flask
import pymongo


class Database:
    """
    Flask extension to create our database connection.

    First obtain a MongoClient, then a Database from that client.
    Working only with that Database, Flask is limited to contents of that DocumentDB database.

    pyMongo.MongoClient internally manages a thread-safe connection pool.
    It internally assigns a connection to each thread.
    This class therefore does not request or release database connections.
    """
    @staticmethod
    def init_app(*, app: flask.Flask,):
        client = pymongo.MongoClient(
            connect=True,
            host=app.config["DOCUMENTDB_HOST"],
            port=app.config["DOCUMENTDB_PORT"],
            directConnection=app.config["DOCUMENTDB_DIRECTCONNECTION"],
            tls=True,
            tlsInsecure=app.config["DOCUMENTDB_TLSINSECURE"],
            username=app.config["DATABASE_USER"],
            password=app.config["DATABASE_PASSWORD"],
        )

        database = client.get_database(app.config["DATABASE_NAME"])

        app.db = database
