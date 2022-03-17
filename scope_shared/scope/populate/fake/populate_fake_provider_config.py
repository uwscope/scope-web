import copy
import faker
from typing import List

import scope.database.providers
import scope.testing.fake_data.fixtures_fake_provider_identity


def create_fake_provider_configs(
    *,
    faker_factory: faker.Faker,
    create_fake: int,
    role: str,
    actions: List[str],
) -> List[dict]:
    created_provider_configs = []
    for _ in range(create_fake):
        created_provider_config = create_fake_provider_config(
            faker_factory=faker_factory,
            role=role,
            actions=actions,
        )
        created_provider_configs.append(created_provider_config)

    return created_provider_configs


def create_fake_provider_config(
    *,
    faker_factory: faker.Faker,
    role: str,
    actions: List[str],
) -> dict:
    # Obtain a fake provider identity, from which we can take necessary fields
    fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
        faker_factory=faker_factory,
    )
    fake_provider_identity = fake_provider_identity_factory()

    # Create the config for creating this fake provider
    fake_provider_config = {
        "name": fake_provider_identity["name"],
        "role": role,
        "actions": copy.deepcopy(actions),
    }

    return fake_provider_config
