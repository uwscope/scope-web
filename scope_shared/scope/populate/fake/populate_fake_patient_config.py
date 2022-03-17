import copy
import faker
from typing import List

import scope.testing.fake_data.fixtures_fake_patient_profile


def create_fake_patient_configs(
    *,
    faker_factory: faker.Faker,
    create_fake: int,
    actions: List[str],
) -> List[dict]:
    created_patient_configs = []
    for _ in range(create_fake):
        created_patient_config = create_fake_patient_config(
            faker_factory=faker_factory,
            actions=actions,
        )
        created_patient_configs.append(created_patient_config)

    return created_patient_configs


def create_fake_patient_config(
    *,
    faker_factory: faker.Faker,
    actions: List[str],
) -> dict:
    # Obtain a fake profile, from which we can take necessary fields
    fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
        faker_factory=faker_factory,
    )
    fake_patient_profile = fake_patient_profile_factory()

    # Create the config for creating this fake patient
    fake_patient_config = {
        "name": fake_patient_profile["name"],
        "MRN": fake_patient_profile["MRN"],
        "actions": copy.deepcopy(actions),
    }

    return fake_patient_config
