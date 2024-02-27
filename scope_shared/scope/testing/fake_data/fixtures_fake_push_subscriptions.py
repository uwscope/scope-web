import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_push_subscriptions_factory(
    *,
    fake_push_subscription_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake push subscription documents.
    """

    def factory() -> List[dict]:
        fake_push_subscriptions = [
            fake_push_subscription_factory() for _ in range(random.randint(1, 5))
        ]

        return fake_push_subscriptions

    return factory


@pytest.fixture(name="data_fake_push_subscriptions_factory")
def fixture_data_fake_push_subscriptions_factory(
    data_fake_push_subscription_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_push_subscriptions_factory.
    """

    unvalidated_factory = fake_push_subscriptions_factory(
        fake_push_subscription_factory=data_fake_push_subscription_factory,
    )

    def factory() -> List[dict]:
        fake_push_subscriptions = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.push_subscriptions_schema,
            data=fake_push_subscriptions,
        )

        return fake_push_subscriptions

    return factory
