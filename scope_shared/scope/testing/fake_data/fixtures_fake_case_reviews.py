import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_case_reviews_factory(
    *,
    fake_case_review_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake case review documents.
    """

    def factory() -> List[dict]:
        fake_case_reviews = [
            fake_case_review_factory() for _ in range(random.randint(1, 5))
        ]

        return fake_case_reviews

    return factory


@pytest.fixture(name="data_fake_case_reviews_factory")
def fixture_data_fake_case_reviews_factory(
    data_fake_case_review_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_case_reviews_factory.
    """

    unvalidated_factory = fake_case_reviews_factory(
        fake_case_review_factory=data_fake_case_review_factory,
    )

    def factory() -> List[dict]:
        fake_case_reviews = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.case_reviews_schema,
            data=fake_case_reviews,
        )

        return fake_case_reviews

    return factory
