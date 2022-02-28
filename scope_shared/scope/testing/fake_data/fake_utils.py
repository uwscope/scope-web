import copy
import jschon
import math
import pprint
import pytest
import random
from typing import List


def fake_enum_value(enum):
    """
    Given an instance of enum.Enum, randomly choose a value.
    """

    return random.choice(list(enum)).value


def fake_enum_flag_values(enum):
    """
    Given an instance of enum.Enum, randomly generate a Boolean flag for each value.
    """

    flags = {}
    for key in enum:
        flags[key.value] = random.choice([True, False])

    return flags


def fake_optional(*, document: dict, optional_keys: List[str]) -> dict:
    """
    Delete optional keys, limiting total rate of missing keys.
    """

    max_missing_rate = 0.2
    max_number_missing = math.ceil(len(optional_keys) * max_missing_rate)
    number_missing = random.randint(0, max_number_missing)
    missing_keys = random.sample(optional_keys, k=number_missing)

    fake_optional_document = copy.deepcopy(document)
    for key in missing_keys:
        del fake_optional_document[key]

    return fake_optional_document


def xfail_for_invalid(*, schema: jschon.JSONSchema, document) -> None:
    """
    Verify a document matches a schema, xfail if it does not.
    """

    schema_result = schema.evaluate(jschon.JSON(document))
    if not schema_result.valid:
        schema_output = schema_result.output("detailed")

        pprint.pprint(document)
        print()
        pprint.pprint(schema_output)

        # Use xfail when reduced verbosity is preferred
        # pytest.xfail("Fake data schema invalid.")

        assert schema_result.valid
