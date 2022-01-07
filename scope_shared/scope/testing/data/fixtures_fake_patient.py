import random
from typing import Callable

import bson.json_util
import bson.objectid
import pytest


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
        # "_id": str(bson.objectid.ObjectId()),
        "type": "identity",
        "_rev": 1,
        "name": _fake_name_factory(),
    }

    # TODO: Verify the schema

    return fake_identity


def data_fake_patient_profile_factory() -> dict:
    fake_profile = {
        # "_id": str(bson.objectid.ObjectId()),
        "type": "patientProfile",
        "_rev": 1,
        "name": "First Last",  # TODO: should be same as identity?
        "MRN": "dummy_MRN",
        "clinicCode": "Neuro",  # clinicCode enum
        "birthdate": "June 13, 1985",  # TODO: date pattern needs to be fixed in schema
        "sex": "Male",  # sex enum
        "gender": "Male",  # gender enum
        "pronoun": "He/Him",  # pronoun enum
        "race": "Black",  # race enum
        "primaryOncologyProvider": data_fake_identity_factory(),
        "primaryCareManager": data_fake_identity_factory(),
        "discussionFlag": {
            "Flag as safety risk": True,
            "Flag for discussion": True,
        },
        "followupSchedule": "1-week follow-up",  # followupSchedule enum
        "depressionTreatmentStatus": "CoCM",  # depressionTreatmentStatus enum
    }

    # TODO: Verify the schema

    return fake_profile


def data_fake_clinical_history_factory() -> dict:
    fake_clinical_history = {
        # "_id": str(bson.objectid.ObjectId()),
        "type": "clinicalHistory",
        "_rev": 1,
        "primaryCancerDiagnosis": "primaryCancerDiagnosis",
        "dateOfCancerDiagnosis": "dateOfCancerDiagnosis",  # TODO: date pattern needs to be fixed in schema
        "currentTreatmentRegimen": {
            "Surgery": True,
            "Chemotherapy": True,
            "Radiation": True,
            "Stem Cell Transplant": True,
            "Immunotherapy": True,
            "CAR-T": True,
            "Endocrine": True,
            "Surveillance": True,
        },
        "currentTreatmentRegimenOther": "currentTreatmentRegimenOther",
        "currentTreatmentRegimenNotes": "currentTreatmentRegimenNotes",
        "psychDiagnosis": "psychDiagnosis",
        "pastPsychHistory": "pastPsychHistory",
        "pastSubstanceUse": "pastSubstanceUse",
        "psychSocialBackground": "psychSocialBackground",
    }

    # TODO: Verify the schema

    return fake_clinical_history


def data_fake_values_inventory_factory() -> dict:
    fake_values_inventory = {
        # "_id": str(bson.objectid.ObjectId()),
        "type": "valuesInventory",
        "_rev": 1,
        "assigned": True,
        "assignedDate": "assignedDate",  # TODO: date pattern needs to be fixed in schema
        "values": [
            {
                "id": "id",
                "name": "name",
                "dateCreated": "",
                "dateEdited": "",
                "lifeareaId": "",
                "activities": [
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                ],
            }
        ],
    }

    # TODO: Verify the schema

    return fake_values_inventory


def data_fake_safety_plan_factory() -> dict:
    fake_safety_plan = {
        "type": "safetyPlan",
        "_rev": 1,
        "assigned": True,
        "assignedDate": "some date",
        "reasonsForLiving": "To stare at Mt. Rainier.",
        "supporters": [
            {
                "contactType": "Person",
                "name": "Name",
                "address": "Address",
                "phoneNumber": "Number",
            }
        ],
    }

    # TODO: Verify the schema

    return fake_safety_plan


def data_fake_patient_factory() -> dict:
    fake_patient = {
        # NOTE: A "patient" exists only as a query composed from other documents.
        # Because a "patient" is never stored to the database, it will not have an "_id".
        # Below `_id` isn't being used anywhere for now except in James' version of CRUD patients code.
        # "_id": str(bson.objectid.ObjectId()),
        "type": "patient",
        "identity": data_fake_identity_factory(),
        "patientProfile": data_fake_patient_profile_factory(),
        "clinicalHistory": data_fake_clinical_history_factory(),  # NOTE: In typescipt, all the keys in clinicalHistory are optional. Chat with James about this.
        "valuesInventory": data_fake_values_inventory_factory(),
        "safetyPlan": data_fake_safety_plan_factory(),
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


@pytest.fixture(name="data_fake_patient_profile_factory")
def fixture_data_fake_profile_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_profile_factory.

    Provides a factory for obtaining data for a fake profile.
    """

    return data_fake_patient_profile_factory


@pytest.fixture(name="data_fake_clinical_history_factory")
def fixture_data_fake_clinical_history_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_clinical_history_factory.

    Provides a factory for obtaining data for a fake clinical history.
    """

    return data_fake_clinical_history_factory


@pytest.fixture(name="data_fake_values_inventory_factory")
def fixture_data_fake_values_inventory_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.

    Provides a factory for obtaining data for a fake values inventory.
    """

    return data_fake_values_inventory_factory


@pytest.fixture(name="data_fake_safety_plan_factory")
def fixture_data_fake_safety_plan_factory() -> Callable[[], dict]:
    """
    Fixture for data_fake_values_inventory_factory.

    Provides a factory for obtaining data for a fake values inventory.
    """

    return data_fake_safety_plan_factory
