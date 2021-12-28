import bson.json_util
import bson.objectid
import pytest
import random
from typing import Callable


def _fake_name_factory() -> str:
    first_names = [
        "Paisley",
        "Vince",
        "Prudence",
        "Floyd",
        "Marty",
        "Yvonne",
        "Russ",
        "Herb",
        "Hannah",
        "Melanie",
        "Dwayne",
        "Clifford",
        "Garth",
        "Rachel",
        "Phoebe",
        "Doug",
        "Mortimer",
        "Heath",
        "Iris",
        "Tony",
    ]

    last_names = [
        "Lowe",
        "Dawson",
        "Porter",
        "Tomlinson",
        "Windrow",
        "Cook",
        "Wolfe",
        "Chapman",
        "Malone",
        "Green",
        "Fairbank",
        "Wood",
        "Miller",
        "Clayton",
        "Russell",
        "Atkinson",
        "Whitehead",
        "Greene",
        "Cannon",
        "Pope",
    ]

    return "{} {}".format(random.choice(first_names), random.choice(last_names))


def data_fake_identity_factory() -> dict:
    fake_identity = {
        "_id": str(bson.objectid.ObjectId()),
        "type": "identity",

        "name": _fake_name_factory(),
    }

    # TODO: Verify the schema

    return fake_identity


def data_fake_profile_factory() -> dict:
    fake_profile = {
        "_id": str(bson.objectid.ObjectId()),
        "type": "profile",

        "MRN": "",  # TODO: populate
        "clinicCode": "",  # TODO: populate
        "birthdate": "",  # TODO: populate
        "sex": "",  # TODO: populate
        "gender": "",  # TODO: populate
        "pronoun": "",  # TODO: populate
        "race": "",  # TODO: populate
        "primaryOncologyProvider": "",  # TODO: populate
        "primaryCareManager": "",  # TODO: "ClinicalSocialWorker"
        "discussionFlags": "",  # TODO: populate
        "followupSchedule": "",  # TODO: populate
        "depressionTreatmentStatus": "",  # TODO: populate
    }

    # TODO: Verify the schema

    return fake_profile


def data_fake_patient_factory() -> dict:
    fake_patient = {
        # TODO: A "patient" exists only as a query composed from other documents.
        #       Because a "patient" is never stored to the database, it will not have an "_id".
        "_id": str(bson.objectid.ObjectId()),
        "type": "patient",

        "identity": data_fake_identity_factory(),
        "profile": data_fake_profile_factory(),
    }

    # TODO: Verify the schema

    return fake_patient


@pytest.fixture(name="data_fake_patient_factory")
def fixture_data_fake_patient_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_factory.

    Provides a factory for obtaining data for a fake patient.
    """

    return data_fake_patient_factory
