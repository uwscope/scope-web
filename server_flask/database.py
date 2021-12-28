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
            # Synchronously initiate the connection
            connect=True,
            # Connect to the provided host
            host=app.config["DOCUMENTDB_HOST"],
            port=app.config["DOCUMENTDB_PORT"],
            # Based on configuration, direct connect or use replica set
            directConnection=app.config["DOCUMENTDB_DIRECTCONNECTION"],
            # DocumentDB requires SSL, configure whether certificates are expected to be valid
            tls=True,
            tlsInsecure=app.config["DOCUMENTDB_TLSINSECURE"],
            # PyMongo defaults to retryable writes, which are not supported by DocumentDB
            # https://docs.aws.amazon.com/documentdb/latest/developerguide/functional-differences.html#functional-differences.retryable-writes
            retryWrites=False,
            # Configure user and password
            username=app.config["DATABASE_USER"],
            password=app.config["DATABASE_PASSWORD"],
        )

        database = client.get_database(app.config["DATABASE_NAME"])

        # Store the database client on the Flask app
        app.database = database
