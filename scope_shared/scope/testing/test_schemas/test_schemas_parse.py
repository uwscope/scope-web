import jschon
from pathlib import Path
from pprint import pprint
import pytest
import scope.schema
from typing import Tuple


SCHEMA_DIR_PATH = Path(Path(__file__).parent, "../../schemas")


@pytest.mark.parametrize(
    ["schema_item"],
    [[schema_item] for schema_item in scope.schema.SCHEMAS.items()],
    ids=[schema_item[0] for schema_item in scope.schema.SCHEMAS.items()],
)
def test_schemas_parse(schema_item: Tuple[str, str]):
    schema_name = schema_item[0]
    schema_file_path = schema_item[1]

    # TODO: Anant fix
    if schema_name == "life_area_value_schema":
        pytest.xfail("Failing to parse: Need Anant to Fix")

    # If a schema failed to parse, parse it now to generate a test failure
    if vars(scope.schema).get(schema_name, None) is None:
        with open(Path(SCHEMA_DIR_PATH, schema_file_path), encoding="utf-8") as f:
            schema_json = f.read()
            pprint(schema_json)
            print("===========")
            schema = jschon.JSONSchema.loads(schema_json)
