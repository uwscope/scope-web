import jschon
import json
from pathlib import Path
import pytest
from typing import Tuple

import scope.schema

SCHEMA_DIR_PATH = Path(Path(__file__).parent, "../../schemas")


@pytest.mark.parametrize(
    ["schema_item"],
    [[schema_item] for schema_item in scope.schema.SCHEMAS.items()],
    ids=[schema_item[0] for schema_item in scope.schema.SCHEMAS.items()],
)
def test_schemas_parse(schema_item: Tuple[str, str]):
    schema_name = schema_item[0]
    schema_file_path = schema_item[1]

    # If a schema failed to parse, parse it now to generate a test failure
    if vars(scope.schema).get(schema_name, None) is None:
        schema_path = Path(SCHEMA_DIR_PATH, schema_file_path)
        with open(schema_path, encoding="utf-8") as f:
            schema_json = json.loads(f.read())

        try:
            schema = jschon.JSONSchema(
                schema_json,
                catalog=scope.schema.CATALOG,
            )
        finally:
            # Schema construction failed, try again in the next generation

            # Although construction of the schema failed,
            # jschon will have already placed the schema in the catalog.
            # Schemas dependent on the failed schema will therefore think it is available.
            # Remove it from the catalog so that dependent schemas fail quickly.
            scope.schema.CATALOG.del_schema(jschon.URI(schema_json["$id"]))
