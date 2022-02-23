from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import Union

import jschon
import pytest
import scope.schema

JSON_DATA_PATH = Path(Path(__file__).parent, "json")


@dataclass(frozen=True)
class ConfigTestJSONSchema:
    name: str
    schema: jschon.JSONSchema
    document_path: Union[Path, str]
    expected_valid: bool


TEST_CONFIGS = [
    # clinicalHistory
    ConfigTestJSONSchema(
        name="clinical-history",
        schema=scope.schema.clinical_history_schema,
        document_path="clinical-history.json",
        expected_valid=True,
    ),
    # identity
    ConfigTestJSONSchema(
        name="identity",
        schema=scope.schema.identity_schema,
        document_path="identity.json",
        expected_valid=True,
    ),
    # patient
    ConfigTestJSONSchema(
        name="patient",
        schema=scope.schema.patient_schema,
        document_path="patient.json",
        expected_valid=True,
    ),
    # profile
    ConfigTestJSONSchema(
        name="patient-profile",
        schema=scope.schema.patient_profile_schema,
        document_path="patient-profile.json",
        expected_valid=True,
    ),
    # safetyPlan
    ConfigTestJSONSchema(
        name="safety-plan-valid-some-properties",
        schema=scope.schema.safety_plan_schema,
        document_path="safety-plan/valid/some-properties.json",
        expected_valid=True,
    ),
    ConfigTestJSONSchema(
        name="safety-plan-valid-distractions-mix-string-and-contact",
        schema=scope.schema.safety_plan_schema,
        document_path="safety-plan/valid/distractions-mix-string-and-contact.json",
        expected_valid=True,
    ),
    ConfigTestJSONSchema(
        name="safety-plan-valid-distractions-string-array",
        schema=scope.schema.safety_plan_schema,
        document_path="safety-plan/valid/distractions-string-array.json",
        expected_valid=True,
    ),
    ConfigTestJSONSchema(
        name="safety-plan-valid-distractions-contact-array",
        schema=scope.schema.safety_plan_schema,
        document_path="safety-plan/valid/distractions-contact-array.json",
        expected_valid=True,
    ),
    # sessions
    ConfigTestJSONSchema(
        name="session-referrals-empty",
        schema=scope.schema.session_schema,
        document_path="session/valid/referrals-empty-list.json",
        expected_valid=True,
    ),
    ConfigTestJSONSchema(
        name="session-referrals-not-empty",
        schema=scope.schema.session_schema,
        document_path="session/valid/referrals-not-empty-list.json",
        expected_valid=True,
    ),
    ConfigTestJSONSchema(
        name="session-referrals-null",
        schema=scope.schema.session_schema,
        document_path="session/invalid/referrals-null.json",
        expected_valid=False,
    ),
    ConfigTestJSONSchema(
        name="session-referrals-missing-referralType",
        schema=scope.schema.session_schema,
        document_path="session/invalid/referrals-missing-referralType.json",
        expected_valid=False,
    ),
    ConfigTestJSONSchema(
        name="sessions",
        schema=scope.schema.sessions_schema,
        document_path="sessions.json",
        expected_valid=True,
    ),
    # valuesInventory
    ConfigTestJSONSchema(
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        document_path="values-inventory.json",
        expected_valid=True,
    ),
]


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_json_schema(config: ConfigTestJSONSchema):
    if config.schema is None:
        pytest.xfail("Schema failed to parse")

    with open(Path(JSON_DATA_PATH, config.document_path), encoding="utf-8") as f:
        json = f.read()

    result = config.schema.evaluate(jschon.JSON.loads(json)).output("detailed")

    if result["valid"] != config.expected_valid:
        if not result["valid"]:
            pprint(json)
            print()
            pprint(result)

    assert result["valid"] == config.expected_valid
