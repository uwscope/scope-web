import random
from datetime import datetime
from typing import Callable

import faker
import pytest
import scope.database.patient.clinical_history
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def fake_clinical_history_factory(
    *, faker_factory: faker.Faker, validate: bool = True
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake patient clinical history documents.
    """

    def factory() -> dict:

        fake_clinical_history = {
            "_type": scope.database.patient.clinical_history.DOCUMENT_TYPE,
            "primaryCancerDiagnosis": faker_factory.text(),
            "dateOfCancerDiagnosis": faker_factory.date(),
            "currentTreatmentRegimen": fake_utils.fake_enum_flag_values(
                scope.testing.fake_data.enums.CancerTreatmentRegimen
            ),
            "currentTreatmentRegimenOther": faker_factory.text(),
            "currentTreatmentRegimenNotes": faker_factory.text(),
            "psychDiagnosis": faker_factory.text(),
            "pastPsychHistory": faker_factory.text(),
        }

        if validate:
            scope.schema.raise_for_invalid(
                schema=scope.schema.clinical_history_schema,
                document=fake_clinical_history,
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

    return fake_clinical_history_factory(
        faker_factory=faker,
        validate=True,
    )
