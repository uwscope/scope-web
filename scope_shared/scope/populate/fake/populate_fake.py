import copy
import faker

import scope.database.patients
import scope.database.providers
import scope.enums
import scope.populate.fake.populate_fake_patient_config
import scope.populate.fake.populate_fake_provider_config


def populate_fake_config(
    *,
    faker_factory: faker,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create any fake patients
    #
    if "create_fake_empty" in populate_config["patients"]:
        created_patient_configs = scope.populate.fake.populate_fake_patient_config.create_fake_patient_configs(
            faker_factory=faker_factory,
            create_fake=populate_config["patients"]["create_fake_empty"],
            actions=[
                "populate_default",
            ],
        )
        del populate_config["patients"]["create_fake_empty"]

        populate_config["patients"]["create"].extend(created_patient_configs)

    #
    # Create any fake patients that will additionally be populated with generated fake data
    #
    if "create_fake_generated" in populate_config["patients"]:
        created_patient_configs = scope.populate.fake.populate_fake_patient_config.create_fake_patient_configs(
            faker_factory=faker_factory,
            create_fake=populate_config["patients"]["create_fake_generated"],
            actions=[
                "populate_default",
                "populate_generated",
            ],
        )
        del populate_config["patients"]["create_fake_generated"]

        populate_config["patients"]["create"].extend(created_patient_configs)

    #
    # Create any fake pyschiatrists
    #
    if "create_fake_psychiatrist" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker_factory,
            create_fake=populate_config["providers"]["create_fake_psychiatrist"],
            role=scope.enums.ProviderRole.Psychiatrist.value,
            actions=[]
        )
        del populate_config["providers"]["create_fake_psychiatrist"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    #
    # Create any fake social workers
    #
    if "create_fake_social_worker" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker_factory,
            create_fake=populate_config["providers"]["create_fake_social_worker"],
            role=scope.enums.ProviderRole.SocialWorker.value,
            actions=[]
        )
        del populate_config["providers"]["create_fake_social_worker"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    #
    # Create any fake study staff
    #
    if "create_fake_study_staff" in populate_config["providers"]:
        created_provider_configs = scope.populate.fake.populate_fake_provider_config.create_fake_provider_configs(
            faker_factory=faker_factory,
            create_fake=populate_config["providers"]["create_fake_study_staff"],
            role=scope.enums.ProviderRole.StudyStaff.value,
            actions=[]
        )
        del populate_config["providers"]["create_fake_study_staff"]

        populate_config["providers"]["create"].extend(created_provider_configs)

    return populate_config
