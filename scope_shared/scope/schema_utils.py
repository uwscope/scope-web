import jschon
import pprint
from typing import List, Union


def assert_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
    expected_valid: bool = True,
):
    result = schema.evaluate(jschon.JSON(data))
    if result.valid != expected_valid:
        schema_output = result.output("detailed")

        pprint.pprint(data)
        print()
        pprint.pprint(schema_output)

    assert result.valid == expected_valid


def raise_for_invalid_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
) -> None:
    """
    Verify a document matches a schema, raise an Error if it does not.
    """

    result = schema.evaluate(jschon.JSON(data))

    if not result.valid:
        raise ValueError(result.output("detailed"))
