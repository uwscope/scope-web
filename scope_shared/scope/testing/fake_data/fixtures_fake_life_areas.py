"""
Life areas are not stored documents.

They are loaded from configuration and used throughout a document set.
"""

import json
from pathlib import Path
import pytest
from typing import Callable, List

APP_CONFIG_LIFE_AREAS_PATH = Path(
    Path(__file__).parent, "../../../../server_flask/app_config/life_areas/"
)


def fake_life_areas_factory() -> Callable[[], List[dict]]:
    """
    Obtain a factory that will provide all life area documents.
    """

    def factory() -> List[dict]:
        fake_life_areas = []

        for path_current in APP_CONFIG_LIFE_AREAS_PATH.iterdir():
            if path_current.match("*.json"):
                with open(path_current) as config_file:
                    config_json = json.load(config_file)
                    fake_life_areas.append(config_json)

        return fake_life_areas

    return factory


@pytest.fixture(name="data_fake_life_areas_factory")
def fixture_data_fake_life_areas_factory(
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_life_areas_factory.
    """

    unvalidated_factory = fake_life_areas_factory()

    def factory() -> List[dict]:
        fake_life_areas = unvalidated_factory()

        # TODO: Need life_areas_schema
        # scope.testing.fake_data.fake_utils.xfail_for_invalid(
        #     schema=scope.schema.life_areas_schema,
        #     document=fake_life_areas,
        # )

        return fake_life_areas

    return factory


@pytest.fixture(name="data_fake_life_areas")
def fixture_data_fake_life_areas(
    *,
    data_fake_life_areas_factory: Callable[[], List[dict]],
) -> List[dict]:
    """
    Fixture for data_fake_life_areas.
    """

    return data_fake_life_areas_factory()
