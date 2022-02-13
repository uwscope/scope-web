from dataclasses import dataclass


@dataclass
class Config:
    SECRET_KEY: str
    """
    SECRET_KEY is required by Flask, used for signing session cookies.
    """

    COGNITO_POOLID: str
    """
    ID of the AWS Cognito user pool.
    """

    COGNITO_CLIENTID: str
    """
    Client ID for AWS Cognito user pool.
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
        cognito_poolid: str,
        cognito_clientid: str,
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
        self.COGNITO_POOLID = cognito_poolid
        self.COGNITO_CLIENTID = cognito_clientid
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
