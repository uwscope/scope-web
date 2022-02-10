from dataclasses import dataclass
from pprint import pprint
from typing import Callable, Union

import faker
import jschon
import pytest
import scope.schema
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_case_review
import scope.testing.fake_data.fixtures_fake_case_reviews
import scope.testing.fake_data.fixtures_fake_clinical_history
import scope.testing.fake_data.fixtures_fake_contact
import scope.testing.fake_data.fixtures_fake_identity
import scope.testing.fake_data.fixtures_fake_life_areas
import scope.testing.fake_data.fixtures_fake_patient_profile
import scope.testing.fake_data.fixtures_fake_referral_status
import scope.testing.fake_data.fixtures_fake_safety_plan
import scope.testing.fake_data.fixtures_fake_session
import scope.testing.fake_data.fixtures_fake_sessions
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
        name="identity",
        schema=scope.schema.identity_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_identity.fake_identity_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="contact",
        schema=scope.schema.contact_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_contact.fake_contact_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="referral-status",
        schema=scope.schema.referral_status_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_referral_status.fake_referral_status_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="life-areas",
        schema=scope.schema.life_areas_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory(),
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
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory(
            faker_factory=faker_factory,
            fake_life_areas=scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory()(),
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
            ),
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="session",
        schema=scope.schema.session_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_session.fake_session_factory(
            faker_factory=faker_factory,
            fake_referral_status_factory=scope.testing.fake_data.fixtures_fake_referral_status.fake_referral_status_factory(
                faker_factory=faker_factory,
            ),
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="sessions",
        schema=scope.schema.sessions_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_sessions.fake_sessions_factory(
            fake_session_factory=scope.testing.fake_data.fixtures_fake_session.fake_session_factory(
                faker_factory=faker_factory,
                fake_referral_status_factory=scope.testing.fake_data.fixtures_fake_referral_status.fake_referral_status_factory(
                    faker_factory=faker_factory,
                ),
            ),
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="case-review",
        schema=scope.schema.case_review_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_case_review.fake_case_review_factory(
            faker_factory=faker_factory,
        ),
        expected_valid=True,
    ),
    ConfigTestFakeDataSchema(
        name="case-reviews",
        schema=scope.schema.case_reviews_schema,
        data_factory=scope.testing.fake_data.fixtures_fake_case_reviews.fake_case_reviews_factory(
            fake_case_review_factory=scope.testing.fake_data.fixtures_fake_case_review.fake_case_review_factory(
                faker_factory=faker_factory,
            ),
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
