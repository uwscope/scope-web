import aws_infrastructure.tasks.ssh
import bson.objectid
import contextlib
import pymongo.database

import scope.config
import scope.database.client
import scope.database.patients


def initialize(
    *,
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
    database_config: scope.config.DatabaseConfig,
):
    """
    Initialize a database, bringing it from non-existent to our expected state (e.g., it will pass all tests).

    Initialization should be idempotent.
    """

    with contextlib.ExitStack() as context_manager:
        # Connect as cluster admin for database initialization
        documentdb_client_admin = scope.database.client.documentdb_client_admin(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            host=documentdb_config.endpoint,
            port=documentdb_config.port,
            direct_connection=True,
            tls_insecure=True,
            admin_user=documentdb_config.admin_user,
            admin_password=documentdb_config.admin_password,
        )

        _initialize_database(
            documentdb_client_admin=documentdb_client_admin,
            database_config=database_config,
        )

        # Connect as database user for continued initialization
        database = scope.database.client.documentdb_client_database(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            host=documentdb_config.endpoint,
            port=documentdb_config.port,
            direct_connection=True,
            tls_insecure=True,
            user=database_config.user,
            password=database_config.password,
            database_name=database_config.name,
        )

        _initialize_database_content(database=database)


def reset(
    *,
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
    database_config: scope.config.DatabaseConfig,
):
    """
    Reset a database, by dropping it then initializing it.
    """

    with contextlib.ExitStack() as context_manager:
        documentdb_client_admin = scope.database.client.documentdb_client_admin(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            host=documentdb_config.endpoint,
            port=documentdb_config.port,
            admin_user=documentdb_config.admin_user,
            admin_password=documentdb_config.admin_password,
        )

        documentdb_client_admin.drop_database(name_or_database=database_config.name)

        initialize(
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
            database_config=database_config,
        )


def _initialize_database(
    *,
    documentdb_client_admin: pymongo.MongoClient,
    database_config: scope.config.DatabaseConfig,
):
    """
    Initialize the database itself, while authenticated as admin.

    Requires creating the user associated with the database.
    """

    database = documentdb_client_admin.get_database(
        name=database_config.name,
    )

    # Ensure the expected database user
    # All DocumentDB users are created in the "admin" database
    result = database.command(
        "usersInfo",
        {
            "user": database_config.user,
            "db": "admin",
        },
    )
    if not result["users"]:
        create_or_update_command = "createUser"
    else:
        create_or_update_command = "updateUser"

    database.command(
        create_or_update_command,
        database_config.user,
        pwd=database_config.password,
        roles=[
            {
                "role": "readWrite",
                "db": database_config.name,
            },
        ],
    )


def _initialize_database_content(
    *,
    database: pymongo.database.Database,
):
    """
    Assuming a database exists, initialize its contents.

    Initialization should be idempotent.
    """

    _initialize_patients_collection(database=database)


def _initialize_patients_collection(*, database: pymongo.database.Database):
    """
    Initialize a patients collection.

    Initialization should be idempotent.
    """

    # Get or create a patients collection
    patients_collection = database.get_collection(
        scope.database.patients.PATIENTS_COLLECTION_NAME
    )

    # Ensure a sentinel document
    result = patients_collection.find_one(
        filter={
            "_type": "sentinel",
        }
    )
    if result is None:
        patients_collection.insert_one(
            {
                "_id": bson.objectid.ObjectId(),
                "_type": "sentinel",
            }
        )
