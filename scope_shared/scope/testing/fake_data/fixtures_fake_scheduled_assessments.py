import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.scheduled_assessments
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_scheduled_assessment(
    *,
    faker_factory: faker.Faker,
    fake_assessment: dict,
) -> List[dict]:
    return [
        {
            "_type": scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
            "dueDate": format_utils.format_date(
                faker_factory.date_between_dates(
                    date_start=datetime.datetime.now() - datetime.timedelta(days=10),
                    date_end=datetime.datetime.now() + datetime.timedelta(days=10),
                )
            ),
            "dueType": fake_utils.fake_enum_value(
                scope.testing.fake_data.enums.DueType
            ),
            "assessmentId": fake_assessment["assessmentId"],
            "completed": random.choice([True, False]),
        }
        for _ in range(random.randint(1, 10))
    ]


def _fake_scheduled_assessments(
    *,
    faker_factory: faker.Faker,
    fake_assessments: List[dict],
) -> List[dict]:
    fake_scheduled_assessments = []
    for fake_assessment in fake_assessments:
        if fake_assessment["assessmentId"] != "mood":
            fake_scheduled_assessments.extend(
                _fake_scheduled_assessment(
                    faker_factory=faker_factory,
                    fake_assessment=fake_assessment,
                )
            )
    return fake_scheduled_assessments


def fake_scheduled_assessment_factory(
    *,
    faker_factory: faker.Faker,
    fake_assessments: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake scheduled assessment document.
    """

    def factory() -> dict:

        fake_scheduled_assessment = random.choice(
            _fake_scheduled_assessments(
                faker_factory=faker_factory,
                fake_assessments=fake_assessments,
            )
        )

        return document_utils.normalize_document(document=fake_scheduled_assessment)

    return factory


def fake_scheduled_assessments_factory(
    *,
    faker_factory: faker.Faker,
    fake_assessments: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled assessment documents.
    """

    def factory() -> dict:

        fake_scheduled_assessments = _fake_scheduled_assessments(
            faker_factory=faker_factory,
            fake_assessments=fake_assessments,
        )

        return document_utils.normalize_documents(documents=fake_scheduled_assessments)

    return factory


@pytest.fixture(name="data_fake_scheduled_assessment_factory")
def fixture_data_fake_scheduled_assessment_factory(
    faker: faker.Faker,
    data_fake_assessments: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_scheduled_assessment_factory.
    """

    unvalidated_factory = fake_scheduled_assessment_factory(
        faker_factory=faker,
        fake_assessments=data_fake_assessments,
    )

    def factory() -> dict:
        fake_scheduled_assessment = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.scheduled_assessment_schema,
            document=fake_scheduled_assessment,
        )

        return fake_scheduled_assessment

    return factory


@pytest.fixture(name="data_fake_scheduled_assessments_factory")
def fixture_data_fake_scheduled_assessments_factory(
    faker: faker.Faker,
    data_fake_assessments: List[dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_assessment_factory.
    """

    unvalidated_factory = fake_scheduled_assessments_factory(
        faker_factory=faker,
        fake_assessments=data_fake_assessments,
    )

    def factory() -> dict:
        fake_scheduled_assessments = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.scheduled_assessments_schema,
            document=fake_scheduled_assessments,
        )

        return fake_scheduled_assessments

    return factory
