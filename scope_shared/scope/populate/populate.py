import copy
import datetime
import faker as _faker
from pathlib import Path
import pymongo.database
import re
import ruamel.yaml
import shutil
from typing import List

import scope.config
import scope.populate.cognito.populate_cognito
import scope.populate.fake.populate_fake
import scope.populate.patient.populate_patient
import scope.populate.provider.populate_provider
import scope.schema
import scope.schema_utils


FAKER_INSTANCE = _faker.Faker(locale="la")


def _prompt_to_continue(
    *,
    prompt: List[str],
) -> bool:
    """
    Display a prompt and return whether to continue.
    """

    # Casefold is applied before matching (i.e., lowercase)
    responses_yes: List[str] = ["", "y"]
    responses_no: List[str] = ["n"]

    # Most lines in the prompt are printed
    for prompt_current in prompt[0:-1]:
        print(prompt_current)

    # Final line is augmented before prompting
    prompt = '{} [Y/n]: '.format(prompt[-1])
    while True:
        response = input(prompt)
        response = response.casefold()

        if response in responses_yes:
            return True
        if response in responses_no:
            return False


def _populate_config_path_sort_key(
    config_path: Path
) -> datetime.datetime:
    """
    Sort key for populate config paths.

    Requires each path point to a file with a datetime encoded in its name.
    """

    return datetime.datetime.strptime(
        re.fullmatch(r"populate_(\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\dZ)\.yaml", config_path.name).group(1),
        "%Y_%m_%d_%H_%M_%SZ"
    )


def _populate_config_path_current(
    *,
    populate_dir_path: Path,
) -> Path:
    """
    Within the provided populate_dir, obtain the path for the current populate config.

    This will be the config which has the greatest datetime embedded in its name.
    """

    # Start with every path in the dir
    config_paths = list(populate_dir_path.iterdir())

    # Filter down to those which match our pattern
    filtered_config_paths = []
    for config_path_current in config_paths:
        if config_path_current.is_file() and re.fullmatch(
            r"populate_(\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\dZ)\.yaml",
            config_path_current.name,
        ):
            filtered_config_paths.append(config_path_current)
    config_paths = filtered_config_paths

    # Sort them
    config_paths = sorted(config_paths, key=_populate_config_path_sort_key, reverse=True)

    return config_paths[0]


def _populate_config_path_update(
    *,
    populate_dir_path: Path
) -> Path:
    """
    Generate a path for storing an update to a populate config.
    """

    return Path(
        populate_dir_path,
        "populate_{}.yaml".format(
            datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%SZ")
        ),
    )


def _populate_config_working_path_sort_key(
    config_working_path: Path
) -> int:
    """
    Sort key for working dir populate config paths.

    Requires each path point to a file with a number encoded in its name.
    """

    return int(re.fullmatch(r"(\d+)\.yaml", config_working_path.name).group(1))


def _populate_config_working_path_current(
    *,
    working_dir_path: Path,
) -> Path:
    """
    Within the provided working_dir, obtain the path for the current populate config.

    This will be the config which has the greatest number embedded in its name.
    """
    # Start with every path in the dir
    config_working_paths = list(working_dir_path.iterdir())

    # Filter down to those which match our pattern
    filtered_config_working_paths = []
    for config_working_path_current in config_working_paths:
        if config_working_path_current.is_file() and re.fullmatch(
            r"(\d+)\.yaml",
            config_working_path_current.name,
        ):
            filtered_config_working_paths.append(config_working_path_current)
    config_working_paths = filtered_config_working_paths

    # Sort them
    config_working_paths = sorted(config_working_paths, key=_populate_config_working_path_sort_key, reverse=True)

    return config_working_paths[0]


def _populate_config_working_path_update(
    *,
    config_working_path: Path
) -> Path:
    """
    Generate a path for storing an update to a working config.
    """

    # Increment the integer embedded in the filename
    existing_value = int(re.fullmatch(r"(\d+)\.yaml", config_working_path.name).group(1))

    return config_working_path.parent.joinpath(
        "{}.yaml".format(
             existing_value + 1
        )
    )


def _working_dir_create(
    *,
    populate_config_path: Path,
    working_dir_path: Path,
):
    """
    Create the working directory in which we'll store each incremental config.

    The directory may already exist, indicating we are resuming a prior execution.
    """
    if not working_dir_path.is_dir():
        working_dir_path.mkdir()
        shutil.copy(src=populate_config_path, dst=working_dir_path.joinpath("0.yaml"))


def _working_dir_path(
    *,
    populate_config_path: Path,
) -> Path:
    """
    Obtain a working directory for a given populate config.
    """
    return Path(
        "{}_work".format(
            populate_config_path.parent.joinpath(
                populate_config_path.stem
            )
        )
    )


def populate(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_dir_path: Path,
) -> None:
    """
    Populate from a provided populate config.

    Return new state of populate config.
    """

    # Configure a YAML object
    yaml = ruamel.yaml.YAML(typ="rt", pure=True)
    yaml.default_flow_style = False

    # Track confirmation throughout populate
    populate_continue_confirmed: bool = True

    # Identify the current config from which to start
    populate_config_path: Path = _populate_config_path_current(populate_dir_path=populate_dir_path)

    # Confirm the configuration
    populate_continue_confirmed = _prompt_to_continue(
        prompt=["Using config '{}'".format(populate_config_path)],
    )
    if not populate_continue_confirmed:
        # Did not start yet, nothing to clean up
        return

    # Ensure a working directory exists
    working_dir_path: Path = _working_dir_path(populate_config_path=populate_config_path)
    _working_dir_create(
        populate_config_path=populate_config_path,
        working_dir_path=working_dir_path,
    )

    # If this is a resumption, obtain confirmation
    populate_config_working_path = _populate_config_working_path_current(working_dir_path=working_dir_path)
    if _populate_config_working_path_sort_key(populate_config_working_path) != 0:
        populate_continue_confirmed = _prompt_to_continue(
            prompt=["Resuming from '{}'".format(populate_config_working_path)],
        )
        if not populate_continue_confirmed:
            # Did not start yet, nothing to clean up
            return

    # Process the working directory
    populate_continue_work_remains: bool = True
    while populate_continue_confirmed and populate_continue_work_remains:
        # Obtain the path of the current working config
        populate_config_working_path = _populate_config_working_path_current(working_dir_path=working_dir_path)

        # Load the current working config
        with open(populate_config_working_path, "r", encoding="utf-8") as f:
            populate_config_yaml = f.read()
            populate_config = yaml.load(populate_config_yaml)

        # Verify the config schema
        scope.schema_utils.raise_for_invalid_schema(
            data=populate_config,
            schema=scope.schema.populate_config_schema,
        )

        populate_continue_confirmed = _prompt_to_continue(
            prompt=["Processing from '{}'".format(populate_config_working_path)]
        )
        if populate_continue_confirmed:
            # Temp do-nothing
            # Temp do-nothing
            # Temp do-nothing
            # Temp do-nothing
            populate_config_updated = copy.deepcopy(populate_config)
            populate_continue_work_remains = _populate_config_working_path_sort_key(populate_config_working_path) < 10
            # Temp do-nothing
            # Temp do-nothing
            # Temp do-nothing
            # Temp do-nothing

            # Store the updated working config
            populate_config_working_updated_path = _populate_config_working_path_update(
                config_working_path=populate_config_working_path
            )
            with open(populate_config_working_updated_path, "w", encoding="utf-8") as f:
                yaml.dump(populate_config_updated, f)

            # Verify the config schema after storing it
            # This will therefore display an error, but not "lose" the new config
            scope.schema_utils.raise_for_invalid_schema(
                data=populate_config_updated,
                schema=scope.schema.populate_config_schema,
            )

    # If we completed all work, store an updated config
    if populate_continue_confirmed:
        if not populate_continue_work_remains:
            populate_config_working_path = _populate_config_working_path_current(working_dir_path=working_dir_path)
            populate_config_update_path = _populate_config_path_update(populate_dir_path=populate_dir_path)
            shutil.copy(src=populate_config_working_path, dst=populate_config_update_path)


    # populate_config = copy.deepcopy(populate_config)
    #
    # #
    # # Expand any creation of fake patients and providers,
    # # then they are populated using the same scripts as "real" patients and providers.
    # #
    # populate_config = scope.populate.fake.populate_fake.populate_fake_config(
    #     faker=FAKER_INSTANCE,
    #     populate_config=populate_config,
    # )
    #
    # #
    # # Execute population of patients
    # #
    # populate_config = (
    #     scope.populate.patient.populate_patient.populate_patients_from_config(
    #         faker=FAKER_INSTANCE,
    #         database=database,
    #         cognito_config=cognito_config,
    #         populate_config=populate_config,
    #     )
    # )
    #
    # #
    # # Execute population of providers
    # #
    # populate_config = _populate_providers_from_config(
    #     database=database,
    #     cognito_config=cognito_config,
    #     populate_config=populate_config,
    # )
    #
    # return populate_config


def _populate_providers_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config: dict,
) -> dict:
    populate_config = copy.deepcopy(populate_config)

    #
    # Create specified providers
    #
    created_providers = scope.populate.provider.populate_provider.create_providers(
        database=database,
        create_providers=populate_config["providers"]["create"],
    )
    populate_config["providers"]["create"] = []
    populate_config["providers"]["existing"].extend(created_providers)

    #
    # Populate provider Cognito accounts
    #
    for provider_current in populate_config["providers"]["existing"]:
        if "account" in provider_current:
            provider_current[
                "account"
            ] = scope.populate.cognito.populate_cognito.populate_account_from_config(
                database=database,
                cognito_config=cognito_config,
                populate_config_account=provider_current["account"],
            )

    #
    # Link provider identities to provider Cognito accounts
    #
    scope.populate.provider.populate_provider.ensure_provider_identities(
        database=database,
        providers=populate_config["providers"]["existing"],
    )

    return populate_config
