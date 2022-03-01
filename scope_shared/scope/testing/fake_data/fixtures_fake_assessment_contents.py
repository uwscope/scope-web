"""
Assessment contents are not stored documents.

They are loaded from configuration and used throughout a document set.
"""

import json
from pathlib import Path
import pytest
from typing import Callable, List

import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils

APP_CONFIG_ASSESSMENTS_PATH = Path(
    Path(__file__).parent, "../../../../server_flask/app_config/assessments/"
)


def fake_assessment_contents_factory() -> Callable[[], List[dict]]:
    """
    Obtain a factory that will provide all assessment content documents.
    """

    def factory() -> List[dict]:
        fake_assessments = []

        for path_current in APP_CONFIG_ASSESSMENTS_PATH.iterdir():
            if path_current.match("*.json"):
                with open(path_current) as config_file:
                    config_json = json.load(config_file)
                    fake_assessments.append(config_json)

        return fake_assessments

    return factory


@pytest.fixture(name="data_fake_assessment_contents_factory")
def fixture_data_fake_assessment_contents_factory() -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_assessment_contents_factory.
    """

    unvalidated_factory = fake_assessment_contents_factory()

    def factory() -> List[dict]:
        fake_assessment_contents = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.assessment_contents_schema,
            data=fake_assessment_contents,
        )

        return fake_assessment_contents

    return factory
