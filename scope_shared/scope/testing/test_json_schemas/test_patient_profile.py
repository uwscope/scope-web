import json
import pathlib

import pytest
from jschon import JSON, URI, JSONSchema, create_catalog
from scope.schema import patient_profile_schema

sample_data_dir = pathlib.Path(__file__).parents[1] / "data/jsons"

patient_profile_data = JSON.loadf(sample_data_dir / "patient-profile.json")


@pytest.mark.parametrize(
    ["schema", "document", "expected_valid"],
    [
        (patient_profile_schema, patient_profile_data, True),
    ],
)
def test_values(schema: JSONSchema, document: JSON, expected_valid: bool):
    result = schema.evaluate(document)
    assert result.output("flag")["valid"] == expected_valid
