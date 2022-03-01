import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_sessions_factory(
    *,
    fake_session_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake session documents.
    """

    def factory() -> List[dict]:
        fake_sessions = [fake_session_factory() for _ in range(random.randint(1, 5))]

        return fake_sessions

    return factory


@pytest.fixture(name="data_fake_sessions_factory")
def fixture_data_fake_sessions_factory(
    data_fake_session_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_sessions_factory.
    """

    unvalidated_factory = fake_sessions_factory(
        fake_session_factory=data_fake_session_factory,
    )

    def factory() -> List[dict]:
        fake_sessions = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.sessions_schema,
            data=fake_sessions,
        )

        return fake_sessions

    return factory
