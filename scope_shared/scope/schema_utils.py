import jschon
import pprint
from typing import List, Union

try:
    import pytest
except ImportError:
    pytest = None


def assert_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
    expected_valid: bool = True,
):
    """
    Assert a document matches a schema.
    """

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
    Verify a document matches a schema, raise ValueError if it does not.
    """

    result = schema.evaluate(jschon.JSON(data))

    if not result.valid:
        raise ValueError(result.output("detailed"))


def xfail_for_invalid_schema(
    *,
    data: Union[dict, List[dict]],
    schema: jschon.JSONSchema,
) -> None:
    """
    Verify a document matches a schema, xfail if it does not.
    """

    result = schema.evaluate(jschon.JSON(data))
    if not result.valid:
        schema_output = result.output("detailed")

        pprint.pprint(data)
        print()
        pprint.pprint(schema_output)

        if pytest:
            pytest.xfail("Invalid Schema.")
        else:
            raise ValueError(schema_output)
