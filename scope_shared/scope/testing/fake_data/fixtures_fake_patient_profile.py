from datetime import datetime
import faker
import random
from typing import Callable

import scope.database.patient.patient_profile
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def fake_patient_profile_factory(
    *,
    faker_factory: faker.Faker,
    validate: bool = True
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake patientProfile documents.
    """
    def factory() -> dict:
        name = faker_factory.name()
        mrn = "{}".format(random.randrange(10000, 1000000))

        fake_patient_profile = {
            "_type": scope.database.patient.patient_profile.DOCUMENT_TYPE,

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

        if validate:
            scope.schema.raise_for_invalid(
                schema=scope.schema.patient_profile_schema,
                document=fake_patient_profile
            )

        return fake_patient_profile

    return factory
