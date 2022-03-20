import datetime
import faker
import pytest
import pytz
import random
from typing import Callable, List

import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

# Keys are not naively optional, see allowable_schedules
OPTIONAL_KEYS = []


def _fake_assessment(
    *,
    faker_factory: faker.Faker,
    assessment_content: dict,
) -> dict:

    fake_assessment = {
        # Assessments have a fixed set of allowable IDs
        "_set_id": assessment_content["id"],
        scope.database.patient.assessments.SEMANTIC_SET_ID: assessment_content["id"],
        "_type": scope.database.patient.assessments.DOCUMENT_TYPE,
    }

    allowable_schedules = [
        {
            "assigned": False,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    faker_factory.date_time_between(
                        start_date=datetime.datetime.now()
                        - datetime.timedelta(days=1 * 30),
                        end_date=datetime.datetime.now(),
                    )
                )
            ),
        },
        # Remove Daily from schema
        # {
        #     "assigned": True,
        #     "assignedDateTime": date_utils.format_datetime(
        #         pytz.utc.localize(
        #             faker_factory.date_time_between(
        #                 start_date=datetime.datetime.now()
        #                 - datetime.timedelta(days=1 * 30),
        #                 end_date=datetime.datetime.now(),
        #             )
        #         )
        #     ),
        #     "frequency": scope.enums.ScheduledItemFrequency.Daily.value,
        # },
        {
            "assigned": True,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    faker_factory.date_time_between(
                        start_date=datetime.datetime.now()
                        - datetime.timedelta(days=1 * 30),
                        end_date=datetime.datetime.now(),
                    )
                )
            ),
            "frequency": random.choice(
                [
                    scope.enums.ScheduledItemFrequency.Weekly.value,
                    scope.enums.ScheduledItemFrequency.Biweekly.value,
                    scope.enums.ScheduledItemFrequency.Monthly.value,
                ]
            ),
            "dayOfWeek": fake_utils.fake_enum_value(scope.enums.DayOfWeek),
        },
    ]

    fake_assessment.update(random.choice(allowable_schedules))

    # Remove a randomly sampled subset of optional parameters.
    fake_assessment = fake_utils.fake_optional(
        document=fake_assessment,
        optional_keys=OPTIONAL_KEYS,
    )

    return fake_assessment


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
            if assessment_content_current["id"] != "mood":
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

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.assessment_schema,
            data=fake_assessment,
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

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.assessments_schema,
            data=fake_assessments,
        )

        return fake_assessments

    return factory
