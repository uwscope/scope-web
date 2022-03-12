import datetime
import faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.mood_logs
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "comment",
]


def fake_mood_log_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake mood log documents.
    """

    def factory() -> dict:
        fake_mood_log = {
            "_type": scope.database.patient.mood_logs.DOCUMENT_TYPE,
            "recordedDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    faker_factory.date_time_between_dates(
                        datetime_start=datetime.datetime.now()
                        - datetime.timedelta(days=6 * 30),
                        datetime_end=datetime.datetime.now(),
                    )
                )
            ),
            "comment": faker_factory.text(),
            "mood": random.randint(0, 10),
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_mood_log = fake_utils.fake_optional(
            document=fake_mood_log,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_mood_log

    return factory


@pytest.fixture(name="data_fake_mood_log_factory")
def fixture_data_fake_mood_log_factory(
    faker: faker.Faker,
    data_fake_referral_status_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_mood_log_factory.
    """

    unvalidated_factory = fake_mood_log_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_mood_log = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.mood_log_schema,
            data=fake_mood_log,
        )

        return fake_mood_log

    return factory
