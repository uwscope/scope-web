from dataclasses import dataclass
import jschon
from pathlib import Path
from pprint import pprint
import pytest
from typing import Union

import scope.schema

JSON_DATA_PATH = Path(Path(__file__).parent, "json")


@dataclass(frozen=True)
class JSONSchemaConfig:
    name: str
    schema: jschon.JSONSchema
    document_path: Union[Path, str]
    expected_valid: bool


TEST_JSON_SCHEMA_CONFIGS = [
    JSONSchemaConfig(
        name="clinical-history",
        schema=scope.schema.clinical_history_schema,
        document_path="clinical-history.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="identity",
        schema=scope.schema.identity_schema,
        document_path="identity.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="patient",
        schema=scope.schema.patient_schema,
        document_path="patient.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="patient-profile",
        schema=scope.schema.patient_profile_schema,
        document_path="patient-profile.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="safety-plan",
        schema=scope.schema.safety_plan_schema,
        document_path="safety-plan.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="session",
        schema=scope.schema.session_schema,
        document_path="session.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="sessions",
        schema=scope.schema.sessions_schema,
        document_path="sessions.json",
        expected_valid=True,
    ),
    JSONSchemaConfig(
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        document_path="values-inventory.json",
        expected_valid=True,
    ),
]


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_JSON_SCHEMA_CONFIGS],
    ids=[config.name for config in TEST_JSON_SCHEMA_CONFIGS],
)
def test_json_schema(config: JSONSchemaConfig):
    result = config.schema.evaluate(
        jschon.JSON.loadf(Path(JSON_DATA_PATH, config.document_path))
    ).output("detailed")

    pprint(result)

    assert result["valid"] == config.expected_valid
