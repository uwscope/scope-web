import bson.json_util
import bson.objectid
import pymongo
import pytest
import random
from typing import Callable


@pytest.fixture(name="data_fake_patient_factory")
def fixture_data_fake_patient_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_factory.

    Provides a factory for obtaining data for a fake patient.
    """

    def factory() -> dict:
        fake_name = "Fake Patient {}".format(
            random.randrange(start=1, stop=10000)
        )

        fake_patient = {
            # TODO: Should this have an ID, or only if it was in the database?
            "_id": str(bson.objectid.ObjectId()),
            "type": "patient",
            "name": fake_name,
        }

        # TODO: Verify the schema

        return fake_patient

    return factory
