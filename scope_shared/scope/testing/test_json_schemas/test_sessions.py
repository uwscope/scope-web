import json
import pathlib

import pytest
from jschon import JSON, URI, JSONSchema, create_catalog
from scope.schema import sessions_schema

sample_data_dir = pathlib.Path(__file__).parents[1] / "data/jsons"

sessions_data = JSON.loadf(sample_data_dir / "sessions.json")


@pytest.mark.parametrize(
    ["schema", "document", "expected_valid"],
    [
        (sessions_schema, sessions_data, True),
    ],
)
def test_identity(schema: JSONSchema, document: JSON, expected_valid: bool):
    result = schema.evaluate(document)
    print(result.output("basic"))
    assert result.output("flag")["valid"] == expected_valid
