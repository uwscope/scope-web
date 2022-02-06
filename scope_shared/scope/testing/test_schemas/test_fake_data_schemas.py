from dataclasses import dataclass
from pprint import pprint
from typing import Callable, Union

import faker
import jschon
import pytest
import scope.schema
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_clinical_history
import scope.testing.fake_data.fixtures_fake_contact
import scope.testing.fake_data.fixtures_fake_life_areas
import scope.testing.fake_data.fixtures_fake_patient_profile
import scope.testing.fake_data.fixtures_fake_safety_plan
import scope.testing.fake_data.fixtures_fake_values_inventory


@dataclass(frozen=True)
class ConfigTestFakeDataSchema:
    name: str
    schema: jschon.JSONSchema
    data_factory: Callable[[], Union[dict, list]]
    expected_valid: bool

    # Used to indicate test is not resolved
    # because it has an issue in data or schema
    XFAIL_TEST_HAS_TODO: bool = False


TEST_ITERATIONS = 100
faker_factory = faker.Faker()

TEST_CONFIGS = [
    ConfigTestFakeDataSchema(
        name="contact",
        schema=scope.schema.contact_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="patient-profile",
        schema=scope.schema.patient_profile_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="clinical-history",
        schema=scope.schema.clinical_history_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_clinical_history.fake_clinical_history_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="safety-plan",
        schema=scope.schema.safety_plan_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_safety_plan.fake_safety_plan_factory(
            faker_factory=faker_factory,
            fake_contact_factory=scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
                faker_factory=faker_factory,
            )
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        # TODO: what schema applies here?
        XFAIL_TEST_HAS_TODO=True,
        name="activity",
        schema=scope.schema.activity_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_activity.data_fake_activity_factory,
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        # TODO: There currently is no schema defined for life areas. I think:
        #       - life-area.json should describe one of the documents found in server_flask/app_config/life_areas.
        #       - life-areas.json should describe a list of such documents.
        XFAIL_TEST_HAS_TODO=True,
        name="life-areas",
        # TODO: This should then be life_areas_schema
        schema=scope.schema.values_inventory_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory(),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        # XFAIL_TEST_HAS_TODO=True,
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory(
            faker_factory=faker_factory,
            life_areas=scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory()(),
        ),
        expected_valid=True,
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

    if config.schema is None:
        pytest.xfail("Schema failed to parse")

    for count in range(TEST_ITERATIONS):
        data = config.data_factory()
        result = config.schema.evaluate(jschon.JSON(data)).output("detailed")

        if result["valid"] != config.expected_valid:
            if not result["valid"]:
                pprint(data)
                print()
                pprint(result)

            assert result["valid"] == config.expected_valid
