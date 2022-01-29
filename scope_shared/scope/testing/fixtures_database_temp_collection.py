import pymongo.collection
import pymongo.database
import pytest
from typing import Callable
from typing import List
import uuid


@pytest.fixture(name="database_temp_collection_factory")
def fixture_database_temp_collection_factory(
    database_client: pymongo.database.Database,
) -> Callable[[], pymongo.collection.Collection]:
    """
    Fixture for temp_collection_client_factory.

    Provides a factory for obtaining a client for a temporary Collection.
    Removes any temporary collections that are created by obtained factory.
    """

    # List of collections created by the factory
    temp_collection_names: List[str] = []

    # Actual factory for obtaining a client for a temporary Collection.
    def factory() -> pymongo.collection.Collection:
        temp_collection_name_create = "temp_collection_{}".format(uuid.uuid4().hex)
        temp_collection_names.append(temp_collection_name_create)

        temp_collection = database_client.get_collection(
            name=temp_collection_name_create
        )

        return temp_collection

    yield factory

    # Remove any created collections
    for temp_collection_name_delete in temp_collection_names:
        database_client.drop_collection(temp_collection_name_delete)
