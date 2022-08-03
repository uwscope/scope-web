import copy
import math
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
        if key in fake_optional_document:
            del fake_optional_document[key]

    return fake_optional_document
