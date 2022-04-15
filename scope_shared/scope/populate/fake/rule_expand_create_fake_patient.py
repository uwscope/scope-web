import copy
from typing import List, Optional

from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.testing.fake_data.fixtures_fake_patient_profile


class ExpandCreateFakePatient(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        if "create_fake_empty" in populate_config["patients"]:
            return _ExpandCreateFakeEmptyAction()

        if "create_fake_generated" in populate_config["patients"]:
            return _ExpandCreateFakeGeneratedAction()

        return None


class _ExpandCreateFakeEmptyAction(PopulateAction):
    def prompt(self) -> List[str]:
        return ["Expand create_fake_empty"]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Retrieve the number we are to create
        number_create_fake: int = populate_config["patients"]["create_fake_empty"]

        # Remove our flag from the configuration
        del populate_config["patients"]["create_fake_empty"]

        # Create the patient configs
        created_patient_configs: List[dict] = []
        for _ in range(number_create_fake):
            # Obtain a fake profile, from which we can take necessary fields
            fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
                faker_factory=populate_context.faker,
            )
            fake_patient_profile = fake_patient_profile_factory()

            # Create the config for this fake patient
            fake_patient_config = {
                "name": fake_patient_profile["name"],
                "MRN": fake_patient_profile["MRN"],
                "actions": copy.deepcopy([]),
            }

            created_patient_configs.append(fake_patient_config)

        # Add them to the config
        populate_config["patients"]["create"].extend(created_patient_configs)

        return populate_config


class _ExpandCreateFakeGeneratedAction(PopulateAction):
    def prompt(self) -> List[str]:
        return ["Expand create_fake_generated"]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Retrieve the number we are to create
        number_create_fake: int = populate_config["patients"]["create_fake_generated"]

        # Remove our flag from the configuration
        del populate_config["patients"]["create_fake_generated"]

        # Create the patient configs
        created_patient_configs: List[dict] = []
        for _ in range(number_create_fake):
            # Obtain a fake profile, from which we can take necessary fields
            fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
                faker_factory=populate_context.faker,
            )
            fake_patient_profile = fake_patient_profile_factory()

            # Create the config for this fake patient
            fake_patient_config = {
                "name": fake_patient_profile["name"],
                "MRN": fake_patient_profile["MRN"],
                "actions": copy.deepcopy(
                    [
                        "populate_generated_data",
                    ]
                ),
            }

            created_patient_configs.append(fake_patient_config)

        # Add them to the config
        populate_config["patients"]["create"].extend(created_patient_configs)

        return populate_config
