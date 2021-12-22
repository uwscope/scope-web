from dataclasses import dataclass


@dataclass
class Config:
    SECRET_KEY: str
    """
    SECRET_KEY is required by Flask, used for signing session cookies.
    """

    DOCUMENTDB_HOST: str
    """
    Host of DocumentDB cluster.
    """

    DOCUMENTDB_PORT: int
    """
    Port of DocumentDB cluster.
    """

    DOCUMENTDB_DIRECTCONNECTION: bool
    """
    Whether to provide the directConnection flag.
    """

    DOCUMENTDB_TLSINSECURE: bool
    """
    Whether to provide the tlsInsecure flag.
    """

    DATABASE_NAME: str
    """
    Name of database.
    """

    DATABASE_USER: str
    """
    User for database connection.
    """

    DATABASE_PASSWORD: str
    """
    Password for database connection.
    """

    def __init__(
        self,
        *,
        secret_key: str,
        documentdb_host: str,
        documentdb_port: int,
        documentdb_directconnection: bool,
        documentdb_tlsinsecure: bool,
        database_name: str,
        database_user: str,
        database_password: str,
    ):
        """
        Using an explicit constructor for naming convention.
        """

        self.SECRET_KEY = secret_key
        self.DOCUMENTDB_HOST = documentdb_host
        self.DOCUMENTDB_PORT = documentdb_port
        self.DOCUMENTDB_DIRECTCONNECTION = documentdb_directconnection
        self.DOCUMENTDB_TLSINSECURE = documentdb_tlsinsecure
        self.DATABASE_NAME = database_name
        self.DATABASE_USER = database_user
        self.DATABASE_PASSWORD = database_password

    #
    # Additional fixed configuration
    #

    JSON_ADD_STATUS: bool = False
    """
    Expected by FlaskJSON. Disables inclusion of "status" field in response body.
    """
