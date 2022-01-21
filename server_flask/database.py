import flask

import scope.documentdb.client


class Database:
    """
    Flask extension to create our database connection.

    Working only with a Database, Flask is limited to contents of that DocumentDB database.

    pyMongo.MongoClient internally manages a thread-safe connection pool.
    It internally assigns a connection to each thread.
    This class therefore does not request or release database connections.
    """
    @staticmethod
    def init_app(*, app: flask.Flask,):
        database = scope.documentdb.client.documentdb_client_database(
            # Connect to the provided host
            host=app.config["DOCUMENTDB_HOST"],
            port=app.config["DOCUMENTDB_PORT"],
            # Based on configuration, direct connect or use replica set
            direct_connection=app.config["DOCUMENTDB_DIRECTCONNECTION"],
            # DocumentDB requires SSL, configure whether certificates are expected to be valid
            tls_insecure=app.config["DOCUMENTDB_TLSINSECURE"],
            # Configure user and password
            user=app.config["DATABASE_USER"],
            password=app.config["DATABASE_PASSWORD"],
            # Desired database
            database_name=app.config["DATABASE_NAME"],
        )

        # Store the database client on the Flask app
        app.database = database
