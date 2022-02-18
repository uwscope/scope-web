import datetime
from typing import Callable

import faker
import pytest
import scope.database.collection_utils as collection_utils
import scope.database.format_utils as format_utils
import scope.database.format_utils
import scope.database.patient.case_reviews
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


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
            "reviewId": collection_utils.generate_unique_id(),
            "date": format_utils.format_date(
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

        fake_utils.xfail_for_invalid(
            schema=scope.schema.case_review_schema,
            document=fake_case_review,
        )

        return fake_case_review

    return factory
