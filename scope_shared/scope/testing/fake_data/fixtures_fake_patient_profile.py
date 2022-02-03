import random
from datetime import datetime
from typing import Callable

import faker
import pytest
import scope.database.patient.patient_profile
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def fake_patient_profile_factory(
    *, faker_factory: faker.Faker, validate: bool = True
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
            "clinicCode": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.ClinicCode
            ),
            "birthdate": datetime.combine(
                faker_factory.date_of_birth(),
                datetime.min.time(),  # 00:00.00.00
            ).isoformat(),
            "sex": fake_utils.fake_enum_value(scope.testing.fake_data.enums.PatientSex),
            "gender": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.PatientGender
            ),
            "pronoun": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.PatientPronoun
            ),
            "race": fake_utils.fake_enum_flag_values(
                scope.testing.fake_data.enums.PatientRace
            ),
            # TODO: identity information
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

        if validate:
            scope.schema.raise_for_invalid(
                schema=scope.schema.patient_profile_schema,
                document=fake_patient_profile,
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

    return fake_patient_profile_factory(
        faker_factory=faker,
        validate=True,
    )
