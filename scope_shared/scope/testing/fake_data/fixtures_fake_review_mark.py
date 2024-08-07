import datetime
import faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.review_marks
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_review_mark_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake recent entry review documents.
    """

    def factory() -> dict:
        fake_review_mark = {
            "_type": scope.database.patient.review_marks.DOCUMENT_TYPE,
            "editedDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    faker_factory.date_time_between_dates(
                        datetime_start=datetime.datetime.now()
                        - datetime.timedelta(weeks=1),
                        datetime_end=datetime.datetime.now(),
                    )
                )
            ),
            "effectiveDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    faker_factory.date_time_between_dates(
                        datetime_start=datetime.datetime.now()
                        - datetime.timedelta(weeks=2),
                        datetime_end=datetime.datetime.now(),
                    )
                )
            ),
            "providerId": faker_factory.name(),
        }

        return fake_review_mark

    return factory


@pytest.fixture(name="data_fake_review_mark_factory")
def fixture_data_fake_review_mark_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_review_mark_factory.
    """

    unvalidated_factory = fake_review_mark_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_review_mark = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.review_mark_schema,
            data=fake_review_mark,
        )

        return fake_review_mark

    return factory
