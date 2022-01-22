import json
import pathlib

import pytest
from jschon import JSON, URI, JSONSchema, create_catalog
from scope.schema import identity_schema

sample_data_dir = pathlib.Path(__file__).parents[1] / "data/jsons"

identity_data = JSON.loadf(sample_data_dir / "identity.json")


@pytest.mark.parametrize(
    ["schema", "document", "expected_valid"],
    [
        (identity_schema, identity_data, True),
    ],
)
def test_identity(schema: JSONSchema, document: JSON, expected_valid: bool):
    result = schema.evaluate(document)
    assert result.output("flag")["valid"] == expected_valid
