import datetime
import faker
import pytest
import pytz
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.database.patient.scheduled_assessments
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_scheduled_assessment(
    *,
    faker_factory: faker.Faker,
    assessment: dict,
) -> dict:
    return {
        "_type": scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
        scope.database.patient.assessments.SEMANTIC_SET_ID: assessment[
            scope.database.patient.assessments.SEMANTIC_SET_ID
        ],
        "dueDate": date_utils.format_date(
            faker_factory.date_between(
                start_date=datetime.date.today() - datetime.timedelta(days=10),
                end_date=datetime.date.today() + datetime.timedelta(days=10),
            )
        ),
        "dueTimeOfDay": random.randint(0, 23),
        "dueDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                faker_factory.date_time_between(
                    start_date=datetime.datetime.utcnow() - datetime.timedelta(days=10),
                    end_date=datetime.datetime.utcnow() + datetime.timedelta(days=10),
                )
            )
        ),
        "reminderDate": date_utils.format_date(
            faker_factory.date_between(
                start_date=datetime.date.today() - datetime.timedelta(days=10),
                end_date=datetime.date.today() + datetime.timedelta(days=10),
            )
        ),
        "reminderTimeOfDay": random.randint(0, 23),
        "reminderDateTime": date_utils.format_datetime(
            pytz.utc.localize(
                faker_factory.date_time_between(
                    start_date=datetime.datetime.utcnow() - datetime.timedelta(days=10),
                    end_date=datetime.datetime.utcnow() + datetime.timedelta(days=10),
                )
            )
        ),
        "completed": random.choice([True, False]),
    }


def fake_scheduled_assessment_factory(
    *,
    faker_factory: faker.Faker,
    assessment: dict,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate a fake scheduled assessment document.
    """

    if scope.database.patient.assessments.SEMANTIC_SET_ID not in assessment:
        raise ValueError(
            'assessment must include "{}".'.format(
                scope.database.patient.assessments.SEMANTIC_SET_ID
            )
        )
    if assessment[scope.database.patient.assessments.SEMANTIC_SET_ID] == "mood":
        raise ValueError(
            '"{}" must not be "{}".'.format(
                scope.database.patient.assessments.SEMANTIC_SET_ID, "mood"
            )
        )

    def factory() -> dict:
        return _fake_scheduled_assessment(
            faker_factory=faker_factory,
            assessment=assessment,
        )

    return factory


def fake_scheduled_assessments_factory(
    *,
    faker_factory: faker.Faker,
    assessment: dict,
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake scheduled assessment documents.
    """

    def factory() -> List[dict]:
        factory = fake_scheduled_assessment_factory(
            faker_factory=faker_factory,
            assessment=assessment,
        )

        fake_scheduled_assessments = []
        for _ in range(random.randint(1, 10)):
            fake_scheduled_assessments.append(factory())

        return fake_scheduled_assessments

    return factory


@pytest.fixture(name="data_fake_scheduled_assessment_factory")
def fixture_data_fake_scheduled_assessment_factory(
    faker: faker.Faker,
    data_fake_assessments_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_scheduled_assessment_factory.
    """

    def factory() -> dict:
        assessments = data_fake_assessments_factory()
        assessments = [
            assessment_current
            for assessment_current in assessments
            if assessment_current[scope.database.patient.assessments.SEMANTIC_SET_ID]
            != "mood"
        ]

        assessment = random.choice(assessments)

        unvalidated_factory = fake_scheduled_assessment_factory(
            faker_factory=faker,
            assessment=assessment,
        )

        fake_scheduled_assessment = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_assessment_schema,
            data=fake_scheduled_assessment,
        )

        return fake_scheduled_assessment

    return factory


@pytest.fixture(name="data_fake_scheduled_assessments_factory")
def fixture_data_fake_scheduled_assessments_factory(
    faker: faker.Faker,
    data_fake_assessments_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_scheduled_assessment_factory.
    """

    def factory() -> List[dict]:
        assessments = data_fake_assessments_factory()
        assessments = [
            assessment_current
            for assessment_current in assessments
            if assessment_current[scope.database.patient.assessments.SEMANTIC_SET_ID]
            != "mood"
        ]

        fake_scheduled_assessments = []
        for assessment_current in assessments:
            unvalidated_factory = fake_scheduled_assessments_factory(
                faker_factory=faker,
                assessment=assessment_current,
            )

            fake_scheduled_assessments.extend(unvalidated_factory())

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.scheduled_assessments_schema,
            data=fake_scheduled_assessments,
        )

        return fake_scheduled_assessments

    return factory
