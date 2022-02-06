import random
from typing import Callable

import faker
import pytest
import scope.database.patient.clinical_history
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_PROPERTIES = [
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
        dateFormat = random.choice([
            "%x",
            "%B %Y",
            "%Y",
        ])
        dateOfCancerDiagnosis = faker_factory.date_object().strftime(dateFormat)

        fake_clinical_history = {
            "_type": scope.database.patient.clinical_history.DOCUMENT_TYPE,
            "primaryCancerDiagnosis": faker_factory.text(),
            "dateOfCancerDiagnosis": dateOfCancerDiagnosis,
            "currentTreatmentRegimen": fake_utils.fake_enum_flag_values(
                scope.testing.fake_data.enums.CancerTreatmentRegimen
            ),
            "currentTreatmentRegimenOther": faker_factory.text(),
            "currentTreatmentRegimenNotes": faker_factory.text(),
            "psychDiagnosis": faker_factory.text(),
            "pastPsychHistory": faker_factory.text(),
            "pastSubstanceUse": faker_factory.text(),
            "psychSocialBackground": faker_factory.text(),
        }

        # Remove a randomly sampled subset of optional parameters.
        for key in faker_factory.random_sample(OPTIONAL_PROPERTIES):
            del fake_clinical_history[key]

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

        scope.testing.fake_data.fake_utils.xfail_for_invalid(
            schema=scope.schema.clinical_history_schema,
            document=fake_clinical_history,
        )

        return fake_clinical_history

    return factory
