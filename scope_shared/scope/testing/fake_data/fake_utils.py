import base64
import copy
import hashlib
import math
import random
import uuid
from typing import List

import jschon
import pytest


def fake_unique_id() -> str:
    """
    Generate a id that:
    - Is guaranteed to be URL safe.
    - Is expected to be unique.

    TODO: Same as _generate_patient_id method in patients model file.
          We may want a general purpose function for this.
          In which case we would then also remove this.
    """

    # Obtain uniqueness
    generated_uuid = uuid.uuid4()
    # Manage length so these don't seem obscenely long
    generated_digest = hashlib.blake2b(generated_uuid.bytes, digest_size=6).digest()
    # Obtain URL safety and MongoDB collection name compatibility.
    generated_base64 = base64.b32encode(generated_digest).decode("ascii").casefold()

    # Remove terminating "=="
    clean_generated_base64 = generated_base64.rstrip("=")

    return clean_generated_base64


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

    result = schema.evaluate(jschon.JSON(document))

    if not result.valid:
        pytest.xfail("Fake data schema invalid.")
