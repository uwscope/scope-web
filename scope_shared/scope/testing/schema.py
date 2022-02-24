import jschon
import pprint
from typing import List, Union


def assert_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
    expected_valid: bool,
):
    schema_result = schema.evaluate(jschon.JSON(data)).output("detailed")
    if schema_result["valid"] != expected_valid:
        pprint.pprint(data)
        print()
        pprint.pprint(schema_result)

    assert schema_result["valid"] == expected_valid
