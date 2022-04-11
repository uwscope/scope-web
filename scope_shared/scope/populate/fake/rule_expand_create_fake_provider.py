import copy
import faker as _faker
from typing import List, Optional

import scope.enums
from scope.populate.types import PopulateAction, PopulateRule
import scope.testing.fake_data.fixtures_fake_provider_identity


class ExpandCreateFakeProvider(PopulateRule):
    faker: _faker.Faker  # Used for faking

    def __init__(
        self,
        *,
        faker: _faker.Faker,
    ):
        self.faker = faker

    def match(self, *, populate_config: dict) -> Optional[PopulateAction]:
        if "create_fake_psychiatrist" in populate_config["providers"]:
            return _ExpandCreateFakePsychiatristAction(
                faker=self.faker,
            )

        if "create_fake_social_worker" in populate_config["providers"]:
            return _ExpandCreateFakeSocialWorkerAction(
                faker=self.faker,
            )

        if "create_fake_study_staff" in populate_config["providers"]:
            return _ExpandCreateFakeStudyStaffAction(
                faker=self.faker,
            )

        return None


class _ExpandCreateFakePsychiatristAction(PopulateAction):
    faker: _faker.Faker  # Used for faking
    actions: List[str]  # List of actions to configure

    def __init__(
        self,
        *,
        faker: _faker.Faker,
    ):
        self.faker = faker

    def prompt(self) -> List[str]:
        return ["Expand create_fake_psychiatrist"]

    def perform(self, *, populate_config: dict) -> dict:
        # Retrieve the number we are to create
        number_create_fake: int = populate_config["providers"]["create_fake_psychiatrist"]

        # Remove our flag from the configuration
        del populate_config["providers"]["create_fake_psychiatrist"]

        # Create the provider configs
        created_provider_configs: List[dict] = []
        for _ in range(number_create_fake):
            # Obtain a fake provider identity, from which we can take necessary fields
            fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
                faker_factory=self.faker,
            )
            fake_provider_identity = fake_provider_identity_factory()

            # Create the config for creating this fake provider
            fake_provider_config = {
                "name": fake_provider_identity["name"],
                "role": scope.enums.ProviderRole.Psychiatrist.value,
                "actions": copy.deepcopy([]),
            }

            created_provider_configs.append(fake_provider_config)

        # Add them to the config
        populate_config["providers"]["create"].extend(created_provider_configs)

        return populate_config


class _ExpandCreateFakeSocialWorkerAction(PopulateAction):
    faker: _faker.Faker  # Used for faking
    actions: List[str]  # List of actions to configure

    def __init__(
        self,
        *,
        faker: _faker.Faker,
    ):
        self.faker = faker

    def prompt(self) -> List[str]:
        return ["Expand create_fake_social_worker"]

    def perform(self, *, populate_config: dict) -> dict:
        # Retrieve the number we are to create
        number_create_fake: int = populate_config["providers"]["create_fake_social_worker"]

        # Remove our flag from the configuration
        del populate_config["providers"]["create_fake_social_worker"]

        # Create the provider configs
        created_provider_configs: List[dict] = []
        for _ in range(number_create_fake):
            # Obtain a fake provider identity, from which we can take necessary fields
            fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
                faker_factory=self.faker,
            )
            fake_provider_identity = fake_provider_identity_factory()

            # Create the config for creating this fake provider
            fake_provider_config = {
                "name": fake_provider_identity["name"],
                "role": scope.enums.ProviderRole.SocialWorker.value,
                "actions": copy.deepcopy([]),
            }

            created_provider_configs.append(fake_provider_config)

        # Add them to the config
        populate_config["providers"]["create"].extend(created_provider_configs)

        return populate_config


class _ExpandCreateFakeStudyStaffAction(PopulateAction):
    faker: _faker.Faker  # Used for faking
    actions: List[str]  # List of actions to configure

    def __init__(
        self,
        *,
        faker: _faker.Faker,
    ):
        self.faker = faker

    def prompt(self) -> List[str]:
        return ["Expand create_fake_study_staff"]

    def perform(self, *, populate_config: dict) -> dict:
        # Retrieve the number we are to create
        number_create_fake: int = populate_config["providers"]["create_fake_study_staff"]

        # Remove our flag from the configuration
        del populate_config["providers"]["create_fake_study_staff"]

        # Create the provider configs
        created_provider_configs: List[dict] = []
        for _ in range(number_create_fake):
            # Obtain a fake provider identity, from which we can take necessary fields
            fake_provider_identity_factory = scope.testing.fake_data.fixtures_fake_provider_identity.fake_provider_identity_factory(
                faker_factory=self.faker,
            )
            fake_provider_identity = fake_provider_identity_factory()

            # Create the config for creating this fake provider
            fake_provider_config = {
                "name": fake_provider_identity["name"],
                "role": scope.enums.ProviderRole.StudyStaff.value,
                "actions": copy.deepcopy([]),
            }

            created_provider_configs.append(fake_provider_config)

        # Add them to the config
        populate_config["providers"]["create"].extend(created_provider_configs)

        return populate_config
