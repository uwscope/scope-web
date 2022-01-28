from datetime import datetime
import random

import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


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

# TODO: these fakes should not be local and redundant in testing

def data_fake_patient_profile_factory() -> dict:
    name = _fake_name_factory()
    mrn = "{}".format(random.randrange(10000, 1000000))

    fake_profile = {
        "_type": "patientProfile",
        "_rev": 1,
        "name": name,
        "MRN": mrn,
        "clinicCode": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.ClinicCode
        ),
        "birthdate": str(
            datetime(
                year=random.randrange(1930, 2000),
                month=random.randrange(1, 13),
                day=random.randrange(1, 29),
            )
        ),
        "sex": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.PatientSex
        ),
        "gender": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.PatientGender
        ),
        "pronoun": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.PatientPronoun
        ),
        "race": fake_utils.fake_enum_flag_values(
            scope.testing.fake_data.enums.PatientRace
        ),
        # "primaryOncologyProvider": data_fake_identity_factory(),
        # "primaryCareManager": data_fake_identity_factory(),
        "discussionFlag": fake_utils.fake_enum_flag_values(
            scope.testing.fake_data.enums.DiscussionFlag
        ),
        "followupSchedule": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.FollowupSchedule
        ),
        "depressionTreatmentStatus": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.DepressionTreatmentStatus
        ),
    }
    #
    # # Verify the schema
    # result = patient_profile_schema.evaluate(JSON(fake_profile))
    # assert result.output("basic")["valid"] == True
    #
    return fake_profile
