import jschon
import pprint
from typing import List, Union


def assert_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
    expected_valid: bool,
):
    schema_result = schema.evaluate(jschon.JSON(data))
    if schema_result.valid != expected_valid:
        schema_output = schema_result.output("detailed")

        pprint.pprint(data)
        print()
        pprint.pprint(schema_output)

    assert schema_result.valid == expected_valid
