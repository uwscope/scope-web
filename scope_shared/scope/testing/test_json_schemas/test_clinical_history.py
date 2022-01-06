import json
import pathlib

import pytest
from jschon import JSON, URI, JSONSchema, create_catalog
from scope.schema import clinical_history_schema

sample_data_dir = pathlib.Path(__file__).parents[1] / "data/jsons"

clinical_history_data = JSON.loadf(sample_data_dir / "clinical-history.json")


@pytest.mark.parametrize(
    ["schema", "document", "expected_valid"],
    [
        (clinical_history_schema, clinical_history_data, True),
    ],
)
def test_values(schema: JSONSchema, document: JSON, expected_valid: bool):
    result = schema.evaluate(document)
    assert result.output("flag")["valid"] == expected_valid
