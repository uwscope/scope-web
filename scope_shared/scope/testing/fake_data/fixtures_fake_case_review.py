import datetime
import faker
import pytest
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.case_reviews
import scope.enums
import scope.schema
import scope.schema_utils


def fake_case_review_factory(
    *,
    faker_factory: faker.Faker,
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake case review documents.
    """

    def factory() -> dict:

        fake_case_review = {
            "_type": scope.database.patient.case_reviews.DOCUMENT_TYPE,
            "date": date_utils.format_date(
                faker_factory.date_between_dates(
                    date_start=datetime.datetime.now() - datetime.timedelta(days=6 * 30)
                )
            ),
            # TODO: identity information
            # "consultingPsychiatrist": fake_identity_factory(),
            "medicationChange": faker_factory.text(),
            "behavioralStrategyChange": faker_factory.text(),
            "referralsChange": faker_factory.text(),
            "otherRecommendations": faker_factory.text(),
            "reviewNote": faker_factory.text(),
        }

        return fake_case_review

    return factory


@pytest.fixture(name="data_fake_case_review_factory")
def fixture_data_fake_case_review_factory(
    faker: faker.Faker,
) -> Callable[[], dict]:
    """
    Fixture for data_fake_case_review_factory.
    """

    unvalidated_factory = fake_case_review_factory(
        faker_factory=faker,
    )

    def factory() -> dict:
        fake_case_review = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.case_review_schema,
            data=fake_case_review,
        )

        return fake_case_review

    return factory
