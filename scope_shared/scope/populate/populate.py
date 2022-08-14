import abc
import copy
import datetime
import faker as _faker
from pathlib import Path
import pymongo.database
import re
import ruamel.yaml
import shutil
from typing import List, Optional

import scope.config
import scope.populate.cognito.rule_create_cognito_account
import scope.populate.cognito.rule_reset_cognito_password
import scope.populate.data.rule_archive_export
import scope.populate.data.rule_archive_migrate
import scope.populate.data.rule_archive_restore
import scope.populate.data.rule_archive_validate
import scope.populate.fake.rule_expand_create_fake_patient
import scope.populate.fake.rule_expand_create_fake_provider
import scope.populate.patient.rule_create_patient
import scope.populate.patient.rule_populate_default_data
import scope.populate.patient.rule_populate_generated_data
import scope.populate.patient.rule_update_patient_identity_cognito_account
import scope.populate.provider.rule_create_provider
import scope.populate.provider.rule_update_provider_identity_cognito_account
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.schema
import scope.schema_utils


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
    prompt = "{} [Y/n]: ".format(prompt[-1])
    while True:
        response = input(prompt)
        response = response.casefold()

        if response in responses_yes:
            return True
        if response in responses_no:
            return False


def _populate_config_path_sort_key(config_path: Path) -> datetime.datetime:
    """
    Sort key for populate config paths.

    Requires each path point to a file with a datetime encoded in its name.
    """

    return datetime.datetime.strptime(
        re.fullmatch(
            r"populate_(\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\dZ)\.yaml", config_path.name
        ).group(1),
        "%Y_%m_%d_%H_%M_%SZ",
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
    config_paths = sorted(
        config_paths, key=_populate_config_path_sort_key, reverse=True
    )

    return config_paths[0]


def _populate_config_path_update(*, populate_dir_path: Path) -> Path:
    """
    Generate a path for storing an update to a populate config.
    """

    return Path(
        populate_dir_path,
        "populate_{}.yaml".format(
            datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%SZ")
        ),
    )


def _populate_config_working_path_sort_key(config_working_path: Path) -> int:
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
    config_working_paths = sorted(
        config_working_paths, key=_populate_config_working_path_sort_key, reverse=True
    )

    return config_working_paths[0]


def _populate_config_working_path_update(*, config_working_path: Path) -> Path:
    """
    Generate a path for storing an update to a working config.
    """

    # Increment the integer embedded in the filename
    existing_value = int(
        re.fullmatch(r"(\d+)\.yaml", config_working_path.name).group(1)
    )

    return config_working_path.parent.joinpath("{}.yaml".format(existing_value + 1))


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
            populate_config_path.parent.joinpath(populate_config_path.stem)
        )
    )


def _populate_rules_create() -> List[PopulateRule]:
    return [
        #
        # Archive management
        #
        scope.populate.data.rule_archive_export.ArchiveExport(),
        scope.populate.data.rule_archive_migrate.ArchiveMigrate(),
        scope.populate.data.rule_archive_restore.ArchiveRestore(),
        scope.populate.data.rule_archive_validate.ArchiveValidate(),
        #
        # Simple rules that expand fake patient and provider creation
        #
        scope.populate.fake.rule_expand_create_fake_patient.ExpandCreateFakePatient(),
        scope.populate.fake.rule_expand_create_fake_provider.ExpandCreateFakeProvider(),
        #
        # Cognito rules
        # - Placing before patient/provider creation allows those to proceed depth-first
        #
        scope.populate.cognito.rule_create_cognito_account.CreateCognitoAccount(),
        scope.populate.cognito.rule_reset_cognito_password.ResetCognitoPassword(),
        #
        # Patient creation rules
        # - These are in reverse order so creation will be depth-first.
        scope.populate.patient.rule_populate_generated_data.PopulateGeneratedData(),
        scope.populate.patient.rule_populate_default_data.PopulateDefaultData(),
        scope.populate.patient.rule_update_patient_identity_cognito_account.UpdatePatientIdentityCognitoAccount(),
        scope.populate.patient.rule_create_patient.CreatePatient(),
        #
        # Provider creation rules
        # - These are in reverse order so creation will be depth-first.
        scope.populate.provider.rule_update_provider_identity_cognito_account.UpdateProviderIdentityCognitoAccount(),
        scope.populate.provider.rule_create_provider.CreateProvider(),
    ]


def _populate_rules_match(
    *,
    populate_rules: List[PopulateRule],
    populate_context: PopulateContext,
    populate_config: dict,
) -> Optional[PopulateAction]:
    """
    Match our ordered list of rules, returning the first match found.
    """

    for populate_rule_current in populate_rules:
        action = populate_rule_current.match(
            populate_context=populate_context,
            populate_config=populate_config,
        )
        if action is not None:
            return action

    return None


def populate_from_dir(
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

    # Configure a faker instance
    faker = _faker.Faker(locale="la")

    # Assemble populate_context
    populate_context = PopulateContext(
        database=database,
        cognito_config=cognito_config,
        faker=faker,
    )

    # Create populate rules
    populate_rules = _populate_rules_create()

    # Track confirmation throughout populate
    populate_continue_confirmed: bool = True

    # Identify the current config from which to start
    populate_config_path: Path = _populate_config_path_current(
        populate_dir_path=populate_dir_path
    )

    # Confirm the configuration
    populate_continue_confirmed = _prompt_to_continue(
        prompt=["Using config '{}'".format(populate_config_path)],
    )
    if not populate_continue_confirmed:
        # Did not start yet, nothing to clean up
        return

    # Ensure a working directory exists
    working_dir_path: Path = _working_dir_path(
        populate_config_path=populate_config_path
    )
    _working_dir_create(
        populate_config_path=populate_config_path,
        working_dir_path=working_dir_path,
    )

    # If this is a resumption, obtain confirmation
    populate_config_working_path = _populate_config_working_path_current(
        working_dir_path=working_dir_path
    )
    if _populate_config_working_path_sort_key(populate_config_working_path) != 0:
        populate_continue_confirmed = _prompt_to_continue(
            prompt=["Resuming from '{}'".format(populate_config_working_path)],
        )
        if not populate_continue_confirmed:
            # Did not start yet, nothing to clean up
            return

    # Process the working directory
    populate_continue_work_remains: bool = True
    while populate_continue_work_remains and populate_continue_confirmed:
        # Obtain the path of the current working config
        populate_config_working_path = _populate_config_working_path_current(
            working_dir_path=working_dir_path
        )

        # Load the current working config
        with open(populate_config_working_path, "r", encoding="utf-8") as f:
            populate_config_yaml = f.read()
            populate_config = yaml.load(populate_config_yaml)

        # Verify the config schema
        scope.schema_utils.raise_for_invalid_schema(
            data=populate_config,
            schema=scope.schema.populate_config_schema,
        )

        # Match our first rule
        populate_action_current = _populate_rules_match(
            populate_rules=populate_rules,
            populate_context=populate_context,
            populate_config=copy.deepcopy(populate_config),
        )
        populate_continue_work_remains = populate_action_current is not None

        # Prompt for confirmation
        if populate_continue_work_remains:
            populate_continue_confirmed = _prompt_to_continue(
                prompt=populate_action_current.prompt()
            )

        if populate_continue_work_remains and populate_continue_confirmed:
            # Perform the action
            populate_config_updated = populate_action_current.perform(
                populate_context=populate_context,
                populate_config=populate_config,
            )

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
            populate_config_working_path = _populate_config_working_path_current(
                working_dir_path=working_dir_path
            )
            populate_config_update_path = _populate_config_path_update(
                populate_dir_path=populate_dir_path
            )
            shutil.copy(
                src=populate_config_working_path, dst=populate_config_update_path
            )
