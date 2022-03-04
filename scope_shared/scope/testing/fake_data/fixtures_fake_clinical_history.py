import faker
import pytest
import random
from typing import Callable

import scope.database.patient.clinical_history
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "primaryCancerDiagnosis",
    "dateOfCancerDiagnosis",
    "currentTreatmentRegimen",
    "currentTreatmentRegimenOther",
    "currentTreatmentRegimenNotes",
    "psychDiagnosis",
    "pastPsychHistory",
    "pastSubstanceUse",
    "psychSocialBackground",
]


def fake_clinical_history_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake clinical history documents.
    """

    def factory() -> dict:
        # This date is not actually a date, is intentionally flexible
        dateFormat = random.choice(
            [
                "%x",
                "%B %Y",
                "%Y",
            ]
        )
        dateOfCancerDiagnosis = faker_factory.date_object().strftime(dateFormat)

        fake_clinical_history = {
            "_type": scope.database.patient.clinical_history.DOCUMENT_TYPE,
            "primaryCancerDiagnosis": faker_factory.text(),
            "dateOfCancerDiagnosis": dateOfCancerDiagnosis,
            "currentTreatmentRegimen": fake_utils.fake_enum_flag_values(
                scope.enums.CancerTreatmentRegimen
            ),
            "currentTreatmentRegimenOther": faker_factory.text(),
            "currentTreatmentRegimenNotes": faker_factory.text(),
            "psychDiagnosis": faker_factory.text(),
            "pastPsychHistory": faker_factory.text(),
            "pastSubstanceUse": faker_factory.text(),
            "psychSocialBackground": faker_factory.text(),
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_clinical_history = fake_utils.fake_optional(
            document=fake_clinical_history,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_clinical_history

    return factory


@pytest.fixture(name="data_fake_clinical_history_factory")
def fixture_data_fake_clinical_history_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_clinical_history_factory.
    """

    unvalidated_factory = fake_clinical_history_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_clinical_history = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.clinical_history_schema,
            data=fake_clinical_history,
        )

        return fake_clinical_history

    return factory
