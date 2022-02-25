import pymongo.database
import scope.config
import scope.database.collection_utils as collection_utils
import scope.database.patients
import scope.database.providers


def ensure_database_exists(
    *,
    documentdb_client_admin: pymongo.MongoClient,
    database_config: scope.config.DatabaseConfig,
):
    """
    Initialize the database itself, while authenticated as admin.

    Requires creating the user associated with the database.

    Initialization should be idempotent.
    """

    database = documentdb_client_admin.get_database(
        name=database_config.name,
    )

    # Determine if the expected database user exists.
    # All DocumentDB users are created in the "admin" database.
    result = database.command(
        "usersInfo",
        {
            "user": database_config.user,
            "db": "admin",
        },
    )
    if not result["users"]:
        create_or_update_user_command = "createUser"
    else:
        create_or_update_user_command = "updateUser"

    # Create or update the expected database user.
    database.command(
        create_or_update_user_command,
        database_config.user,
        pwd=database_config.password,
        roles=[
            {
                "role": "readWrite",
                "db": database_config.name,
            },
        ],
    )


def ensure_database_initialized(
    *,
    database: pymongo.database.Database,
):
    """
    Assuming a database exists, initialize its contents.

    Initialization should be idempotent.
    """

    _initialize_patient_identity_collection(database=database)
    _initialize_provider_identity_collection(database=database)


def _initialize_patient_identity_collection(*, database: pymongo.database.Database):
    """
    Initialize a patients collection.

    Initialization should be idempotent.
    """

    # Ensure a patient identity collection
    patient_identity_collection = database.get_collection(
        scope.database.patients.PATIENT_IDENTITY_COLLECTION
    )

    # Ensure the expected index
    collection_utils.ensure_index(collection=patient_identity_collection)

    # Ensure a sentinel document in that collection
    result = collection_utils.get_singleton(
        collection=patient_identity_collection,
        document_type="sentinel",
    )
    if result is None:
        collection_utils.put_singleton(
            collection=patient_identity_collection,
            document_type="sentinel",
            document={},
        )


def _initialize_provider_identity_collection(*, database: pymongo.database.Database):
    """
    Initialize a providers collection.

    Initialization should be idempotent.
    """

    # Ensure a provider identity collection
    provider_identity_collection = database.get_collection(
        scope.database.providers.PROVIDER_IDENTITY_COLLECTION
    )

    # Ensure the expected index
    collection_utils.ensure_index(collection=provider_identity_collection)

    # Ensure a sentinel document in that collection
    result = collection_utils.get_singleton(
        collection=provider_identity_collection,
        document_type="sentinel",
    )
    if result is None:
        collection_utils.put_singleton(
            collection=provider_identity_collection,
            document_type="sentinel",
            document={},
        )
