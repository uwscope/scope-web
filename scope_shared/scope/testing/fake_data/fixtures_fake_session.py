import datetime
import faker
import pytest
import random
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.sessions
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_session_factory(
    *,
    faker_factory: faker.Faker,
    fake_referral_status_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake session documents.
    """

    def factory() -> dict:

        fake_session = {
            "_type": scope.database.patient.sessions.DOCUMENT_TYPE,
            "date": date_utils.format_date(
                faker_factory.date_between_dates(
                    date_start=datetime.datetime.now() - datetime.timedelta(days=6 * 30)
                )
            ),
            "sessionType": fake_utils.fake_enum_value(scope.enums.SessionType),
            "billableMinutes": random.choice([30, 45, 60, 80]),
            "medicationChange": faker_factory.text(),
            "currentMedications": faker_factory.text(),
            "behavioralStrategyChecklist": fake_utils.fake_enum_flag_values(
                scope.enums.BehavioralStrategyChecklist
            ),
            "behavioralStrategyOther": faker_factory.text(),
            "behavioralActivationChecklist": fake_utils.fake_enum_flag_values(
                scope.enums.BehavioralActivationChecklist
            ),
            "referrals": [
                fake_referral_status_factory() for _ in range(random.randint(0, 5))
            ],
            "otherRecommendations": faker_factory.text(),
            "sessionNote": faker_factory.text(),
        }

        return fake_session

    return factory


@pytest.fixture(name="data_fake_session_factory")
def fixture_data_fake_session_factory(
    faker: faker.Faker,
    data_fake_referral_status_factory: Callable[[], dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_session_factory.
    """

    unvalidated_factory = fake_session_factory(
        faker_factory=faker,
        fake_referral_status_factory=data_fake_referral_status_factory,
    )

    def factory() -> dict:
        fake_session = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.session_schema,
            data=fake_session,
        )

        return fake_session

    return factory
