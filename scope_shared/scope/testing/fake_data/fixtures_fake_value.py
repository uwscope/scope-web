import datetime
import faker as _faker
import pytest
import pytz
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.values
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_value_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake value documents.
    """

    def factory() -> dict:
        datetime_now = datetime.datetime.now()

        fake_value = {
            "_type": scope.database.patient.values.DOCUMENT_TYPE,
            "name": faker.text(),
            "editedDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime_now,
                )
            ),
            "lifeareaId": fake_utils.fake_enum_value(scope.enums.LifeAreaID),
        }

        return fake_value

    return factory


@pytest.fixture(name="data_fake_value_factory")
def fixture_data_fake_value_factory(
    *,
    faker: _faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_value_factory.
    """

    unvalidated_factory = fake_value_factory(
        faker=faker,
    )

    def factory() -> dict:
        fake_value = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.value_schema,
            data=fake_value,
        )

        return fake_value

    return factory
