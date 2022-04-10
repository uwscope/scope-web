import copy
import faker as _faker

import scope.database.patients
import scope.database.providers
import scope.enums
import scope.populate.fake.populate_fake_provider_config


def populate_fake_config(
    *,
    faker: _faker,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create any fake pyschiatrists
    #
    if "create_fake_psychiatrist" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker,
            create_fake=populate_config["providers"]["create_fake_psychiatrist"],
            role=scope.enums.ProviderRole.Psychiatrist.value,
            actions=[],
        )
        del populate_config["providers"]["create_fake_psychiatrist"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    #
    # Create any fake social workers
    #
    if "create_fake_social_worker" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker,
            create_fake=populate_config["providers"]["create_fake_social_worker"],
            role=scope.enums.ProviderRole.SocialWorker.value,
            actions=[],
        )
        del populate_config["providers"]["create_fake_social_worker"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    #
    # Create any fake study staff
    #
    if "create_fake_study_staff" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker,
            create_fake=populate_config["providers"]["create_fake_study_staff"],
            role=scope.enums.ProviderRole.StudyStaff.value,
            actions=[],
        )
        del populate_config["providers"]["create_fake_study_staff"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    return populate_config
