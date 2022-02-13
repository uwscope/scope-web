import pytest
import random


@pytest.fixture(autouse=True)
def faker_seed():
    """
    By default, faker resets its seed to 0 before every test.
    That provides more deterministic tests, but we would prefer more coverage over time.
    The "consistency" of fake data was also sometimes confusing in a development database.
    """
    return random.randint(0, 2**32)
