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
    assessment_content: dict,
) -> dict:
    return {
        # Assessments have a fixed set of allowable IDs
        "_set_id": assessment_content["id"],
        scope.database.patient.assessments.SEMANTIC_SET_ID: assessment_content["id"],

        "_type": scope.database.patient.assessments.DOCUMENT_TYPE,
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


def fake_assessment_factory(
    *,
    faker_factory: faker.Faker,
    assessment_content: dict,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake assessment document.
    """

    def factory() -> dict:
        fake_assessment = _fake_assessment(
            faker_factory=faker_factory,
            assessment_content=assessment_content,
        )

        return fake_assessment

    return factory


def fake_assessments_factory(
    *,
    faker_factory: faker.Faker,
    assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake assessment documents.
    """

    def factory() -> List[dict]:
        # TODO: Should assessment_contents be sampled down

        fake_assessments = []
        for assessment_content_current in assessment_contents:
            fake_assessment = _fake_assessment(
                faker_factory=faker_factory,
                assessment_content=assessment_content_current,
            )
            fake_assessments.append(fake_assessment)

        return fake_assessments

    return factory


@pytest.fixture(name="data_fake_assessment_factory")
def fixture_data_fake_assessment_factory(
    faker: faker.Faker,
    data_fake_assessments_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_assessment_factory.
    """

    def factory() -> dict:
        fake_assessments = data_fake_assessments_factory()

        fake_assessment = random.choice(fake_assessments)

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessment_schema,
            document=fake_assessment,
        )

        return fake_assessment

    return factory


@pytest.fixture(name="data_fake_assessments_factory")
def fixture_data_fake_assessments_factory(
    faker: faker.Faker,
    data_fake_assessment_contents_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_assessments_factory.
    """

    assessment_contents = data_fake_assessment_contents_factory()

    unvalidated_factory = fake_assessments_factory(
        faker_factory=faker,
        assessment_contents=assessment_contents,
    )

    def factory() -> List[dict]:
        fake_assessments = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessments_schema,
            document=fake_assessments,
        )

        return fake_assessments

    return factory
