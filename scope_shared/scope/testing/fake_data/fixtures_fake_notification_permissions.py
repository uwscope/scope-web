import faker
import pytest
import random
from typing import Callable

import scope.database.patient.notification_permissions
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_notification_permissions_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake notification permissions documents.
    """

    def factory() -> dict:
        fake_notification_permissions = {
            "_type": scope.database.patient.notification_permissions.DOCUMENT_TYPE,
            "enablePushNotification": random.choice([True, False]),
        }

        return fake_notification_permissions

    return factory


@pytest.fixture(name="data_fake_notification_permissions_factory")
def fixture_data_fake_notification_permissions_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_notification_permissions_factory.
    """

    unvalidated_factory = fake_notification_permissions_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_notification_permissions = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.notification_permissions_schema,
            data=fake_notification_permissions,
        )

        return fake_notification_permissions

    return factory
