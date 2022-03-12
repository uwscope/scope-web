"""
Referral status are not stored documents.

They are generated and stored as elements of other documents.
"""

import faker
import pytest
from typing import Callable

import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

OPTIONAL_KEYS = [
    "referralOther",
]


def fake_referral_status_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake referral status documents.
    """

    def factory() -> dict:
        fake_referral_status = {
            "referralType": fake_utils.fake_enum_value(scope.enums.Referral),
            "referralStatus": fake_utils.fake_enum_value(scope.enums.ReferralStatus),
            "referralOther": faker_factory.text(),
        }

        # Remove a randomly sampled subset of optional parameters.
        fake_referral_status = fake_utils.fake_optional(
            document=fake_referral_status,
            optional_keys=OPTIONAL_KEYS,
        )

        return fake_referral_status

    return factory


@pytest.fixture(name="data_fake_referral_status_factory")
def fixture_data_fake_referral_status_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_referral_status_factory.
    """
    unvalidated_factory = fake_referral_status_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_referral_status = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.referral_status_schema,
            data=fake_referral_status,
        )

        return fake_referral_status

    return factory
