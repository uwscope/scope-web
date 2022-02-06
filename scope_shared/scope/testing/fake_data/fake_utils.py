import jschon
import random
import pytest


def fake_boolean_value() -> bool:
    return random.choice([True, False])


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


def fake_sample_random_values(values: list) -> list:
    n = random.randint(0, len(values))
    return random.sample(values, n)


def xfail_for_invalid(*, schema: jschon.JSONSchema, document) -> None:
    """
    Verify a document matches a schema, xfail if it does not.
    """

    result = schema.evaluate(jschon.JSON(document))

    if not result.valid:
        pytest.xfail("Fake data schema invalid.")
