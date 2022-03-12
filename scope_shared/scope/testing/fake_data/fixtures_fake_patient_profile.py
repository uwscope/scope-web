import faker
import pytest
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.patient_profile
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "clinicCode",
    "birthdate",
    "sex",
    "gender",
    "pronoun",
    "race",
    # "primaryOncologyProvider",
    # "primaryCareManager",
    "discussionFlag",
    "followupSchedule",
    "depressionTreatmentStatus",
]


def fake_patient_profile_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake patient profile documents.
    """

    def factory() -> dict:
        name = "{} {}".format(faker_factory.first_name(), faker_factory.last_name())
        mrn = "{}".format(random.randrange(10000, 1000000))

        fake_patient_profile = {
            "_type": scope.database.patient.patient_profile.DOCUMENT_TYPE,
            "name": name,
            "MRN": mrn,
            "clinicCode": fake_utils.fake_enum_value(scope.enums.ClinicCode),
            "birthdate": date_utils.format_date(
                faker_factory.date_of_birth(),
            ),
            "sex": fake_utils.fake_enum_value(scope.enums.PatientSex),
            "gender": fake_utils.fake_enum_value(scope.enums.PatientGender),
            "pronoun": fake_utils.fake_enum_value(scope.enums.PatientPronoun),
            "race": fake_utils.fake_enum_flag_values(scope.enums.PatientRace),
            # TODO: identity information
            # "primaryOncologyProvider": data_fake_identity_factory(),
            # "primaryCareManager": data_fake_identity_factory(),
            "discussionFlag": fake_utils.fake_enum_flag_values(
                scope.enums.DiscussionFlag
            ),
            "followupSchedule": fake_utils.fake_enum_value(
                scope.enums.FollowupSchedule
            ),
            "depressionTreatmentStatus": fake_utils.fake_enum_value(
                scope.enums.DepressionTreatmentStatus
            ),
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_patient_profile = scope.testing.fake_data.fake_utils.fake_optional(
            document=fake_patient_profile,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_patient_profile

    return factory


@pytest.fixture(name="data_fake_patient_profile_factory")
def fixture_data_fake_patient_profile_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_patient_profile_factory.
    """

    unvalidated_factory = fake_patient_profile_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_patient_profile = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.patient_profile_schema,
            data=fake_patient_profile,
        )

        return fake_patient_profile

    return factory
