import datetime
from lorem.text import TextLorem
import random
from typing import List

shortLorem = TextLorem(srange=(4, 8), prange=(1, 3))

# TODO: still unclear how to handle references


def data_fake_activity_factory() -> dict:
    fake_activity = {
        "_type": "activity",
        "name": shortLorem.sentence(),
        "value": shortLorem.sentence(),
        "lifeareaId": shortLorem.sentence(),
        "startDate": str(
            datetime.datetime(
                random.randrange(1930, 2000),
                random.randrange(1, 13),
                random.randrange(1, 28),
            )
        ),
        "timeOfDay": random.randrange(1, 25),
        "hasReminder": random.choice([True, False]),
        "reminderTimeOfDay": random.randrange(1, 25),
        "hasRepetition": random.choice([True, False]),
        "repeatDayFlags": "",  # TODO: Check this property with Jina.
        "isActive": random.choice([True, False]),
        "isDeleted": random.choice([True, False]),
    }

    return fake_activity


def data_fake_activities_factory(number_of_activities: int) -> List[dict]:
    fake_activities = []

    for count in range(number_of_activities):
        fake_activity = data_fake_activity_factory()

        fake_activities.append(fake_activity)

    return fake_activities
