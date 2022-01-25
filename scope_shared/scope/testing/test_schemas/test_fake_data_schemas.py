from dataclasses import dataclass
import jschon
from pprint import pprint
import pytest
from typing import Callable

import scope.schema
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_life_areas
import scope.testing.fake_data.fixtures_fake_values_inventory


@dataclass(frozen=True)
class ConfigTestFakeDataSchema:
    name: str
    schema: jschon.JSONSchema
    data_factory: Callable[[], dict]
    expected_valid: bool
    # Used to indicate test is not resolved
    # because it has an issue in data or schema
    XFAIL_TEST_HAS_TODO: bool = False


TEST_CONFIGS = [
    ConfigTestFakeDataSchema(
        name="activity",
        schema=scope.schema.activity_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_activity.data_fake_activity_factory,
        expected_valid=True,
        # TODO: what schema applies here?
        XFAIL_TEST_HAS_TODO=True
    ),
    ConfigTestFakeDataSchema(
        name="life-areas",
        schema=scope.schema.values_inventory_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory,
        expected_valid=True,
        # TODO: what schema applies here?
        XFAIL_TEST_HAS_TODO=True
    ),
    ConfigTestFakeDataSchema(
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory,
        expected_valid=True,
        XFAIL_TEST_HAS_TODO=True
    ),
]


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_fake_data_schema(config: ConfigTestFakeDataSchema):
    if config.XFAIL_TEST_HAS_TODO:
        pytest.xfail("Test has TODO in data or schema.")

    data = config.data_factory()

    result = config.schema.evaluate(
        jschon.JSON(data)
    ).output("detailed")

    pprint(result)

    assert result["valid"] == config.expected_valid
