import json
import pathlib

import pytest
from jschon import JSON, URI, JSONSchema, create_catalog
from scope.schema import session_schema

sample_data_dir = pathlib.Path(__file__).parents[1] / "data/jsons"

session_data = JSON.loadf(sample_data_dir / "session.json")


@pytest.mark.parametrize(
    ["schema", "document", "expected_valid"],
    [
        (session_schema, session_data, True),
    ],
)
def test_identity(schema: JSONSchema, document: JSON, expected_valid: bool):
    result = schema.evaluate(document)
    # print(result.output("detailed"))
    assert result.output("flag")["valid"] == expected_valid
