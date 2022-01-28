import random


def fake_enum_value(enum):
    return random.choice(list(enum)).value


def fake_enum_flag_values(enum):
    flags = {}
    for key in enum:
        flags[key.value] = random.choice([True, False])

    return flags
