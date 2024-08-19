import pytest
import random
from typing import Callable, List

import scope.schema
import scope.schema_utils


def fake_review_marks_factory(
    *,
    fake_review_mark_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake recent entry review documents.
    """

    def factory() -> List[dict]:
        fake_review_marks = [
            fake_review_mark_factory() for _ in range(random.randint(1, 5))
        ]

        return fake_review_marks

    return factory


@pytest.fixture(name="data_fake_review_marks_factory")
def fixture_data_fake_review_marks_factory(
    data_fake_review_mark_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_review_marks_factory.
    """

    unvalidated_factory = fake_review_marks_factory(
        fake_review_mark_factory=data_fake_review_mark_factory,
    )

    def factory() -> List[dict]:
        fake_review_marks = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.review_marks_schema,
            data=fake_review_marks,
        )

        return fake_review_marks

    return factory
