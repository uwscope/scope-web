import datetime
import faker
import pytest
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.push_subscriptions
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_push_subscription_factory(
    *,
    faker_factory: faker.Faker,
    fake_referral_status_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake push subscription documents.
    """

    def factory() -> dict:
        fake_push_subscription = {
            "_type": scope.database.patient.push_subscriptions.DOCUMENT_TYPE,
            "endpoint": faker_factory.url(),
            "expirationTime": random.choice([faker_factory.random_number(), None]),
            "keys": {
                "p256dh": faker_factory.text(),
                "auth": faker_factory.text(),
            },
        }

        return fake_push_subscription

    return factory


@pytest.fixture(name="data_fake_push_subscription_factory")
def fixture_data_fake_push_subscription_factory(
    faker: faker.Faker,
    data_fake_referral_status_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_push_subscription_factory.
    """

    unvalidated_factory = fake_push_subscription_factory(
        faker_factory=faker,
        fake_referral_status_factory=data_fake_referral_status_factory,
    )

    def factory() -> dict:
        fake_push_subscription = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.push_subscription_schema,
            data=fake_push_subscription,
        )

        return fake_push_subscription

    return factory
