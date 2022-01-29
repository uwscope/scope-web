import random


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
