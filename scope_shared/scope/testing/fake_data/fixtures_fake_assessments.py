import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.assessments

import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_assessment(
    *,
    faker_factory: faker.Faker,
    fake_assessment_content: dict,
) -> dict:
    return {
        "_type": scope.database.patient.assessments.DOCUMENT_TYPE,
        # TODO: SET semantic set id because scheduled assessment and assessment log needs it
        scope.database.patient.assessments.SEMANTIC_SET_ID: fake_assessment_content[
            "id"
        ],
        "assigned": random.choice([True, False]),
        "assignedDate": format_utils.format_date(
            faker_factory.date_between_dates(
                date_start=datetime.datetime.now(),
                date_end=datetime.datetime.now() + datetime.timedelta(days=1 * 30),
            )
        ),
        "frequency": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.AssessmentFrequency
        ),
        "dayOfWeek": fake_utils.fake_enum_value(
            scope.testing.fake_data.enums.DayOfWeek
        ),
    }


def _fake_assessments(
    *,
    faker_factory: faker.Faker,
    fake_assessment_contents: List[dict],
):
    return [
        _fake_assessment(
            faker_factory=faker_factory,
            fake_assessment_content=fake_assessment_content,
        )
        for fake_assessment_content in fake_assessment_contents
    ]


def fake_assessment_factory(
    *,
    faker_factory: faker.Faker,
    fake_assessment_contents: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake assessment document.
    """

    def factory() -> dict:

        fake_assessment = random.choice(
            _fake_assessments(
                faker_factory=faker_factory,
                fake_assessment_contents=fake_assessment_contents,
            )
        )

        return document_utils.normalize_document(document=fake_assessment)

    return factory


def fake_assessments_factory(
    *,
    faker_factory: faker.Faker,
    fake_assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake assessment documents.
    """

    def factory() -> dict:

        fake_assessments = _fake_assessments(
            faker_factory=faker_factory,
            fake_assessment_contents=fake_assessment_contents,
        )

        return document_utils.normalize_documents(documents=fake_assessments)

    return factory


@pytest.fixture(name="data_fake_assessment_factory")
def fixture_data_fake_assessment_factory(
    faker: faker.Faker,
    data_fake_assessment_contents: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_assessment_factory.
    """

    unvalidated_factory = fake_assessment_factory(
        faker_factory=faker,
        fake_assessment_contents=data_fake_assessment_contents,
    )

    def factory() -> dict:
        fake_assessment = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessment_schema,
            document=fake_assessment,
        )

        return fake_assessment

    return factory


@pytest.fixture(name="data_fake_assessments_factory")
def fixture_data_fake_assessments_factory(
    faker: faker.Faker,
    data_fake_assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_assessments_factory.
    """

    unvalidated_factory = fake_assessments_factory(
        faker_factory=faker,
        fake_assessment_contents=data_fake_assessment_contents,
    )

    def factory() -> dict:
        fake_assessments = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessments_schema,
            document=fake_assessments,
        )

        return fake_assessments

    return factory


@pytest.fixture(name="data_fake_assessments")
def fixture_data_fake_assessments(
    *,
    data_fake_assessments_factory: Callable[[], List[dict]],
) -> dict:
    """
    Fixture for data_fake_assessments.
    """

    return data_fake_assessments_factory()
