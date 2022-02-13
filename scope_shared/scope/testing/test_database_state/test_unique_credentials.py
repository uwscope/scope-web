import itertools
import pytest
from typing import List

import scope.config


def test_unique_documentdb_credentials(
    request: pytest.FixtureRequest,
):
    """
    Ensure each DocumentDB configuration has unique credentials.
    """

    if "UNIQUE_DOCUMENTDB_CONFIGS" in request.module.__dict__:
        documentdb_configs: List[
            scope.config.DocumentDBConfig
        ] = request.module.UNIQUE_DOCUMENTDB_CONFIGS
    else:
        raise ImportError(name="UNIQUE_DOCUMENTDB_CONFIGS not found in test module.")

    for (
        documentdb_config_current,
        documentdb_config_different,
    ) in itertools.combinations(documentdb_configs, 2):
        assert (
            documentdb_config_current.admin_user
            != documentdb_config_different.admin_user
        )
        assert (
            documentdb_config_current.admin_password
            != documentdb_config_different.admin_password
        )


def test_unique_database_credentials(
    request: pytest.FixtureRequest,
):
    """
    Ensure each database configuration has unique credentials.

    This includes uniqueness relative to DocumentDB configurations.
    """

    if "UNIQUE_DOCUMENTDB_CONFIGS" in request.module.__dict__:
        documentdb_configs: List[
            scope.config.DocumentDBConfig
        ] = request.module.UNIQUE_DOCUMENTDB_CONFIGS
    else:
        raise ImportError(name="UNIQUE_DOCUMENTDB_CONFIGS not found in test module.")

    if "UNIQUE_DATABASE_CONFIGS" in request.module.__dict__:
        database_configs: List[
            scope.config.DatabaseConfig
        ] = request.module.UNIQUE_DATABASE_CONFIGS
    else:
        raise ImportError(name="UNIQUE_DATABASE_CONFIGS not found in test module.")

    for database_config_current in database_configs:
        for documentdb_config_current in documentdb_configs:
            assert database_config_current.user != documentdb_config_current.admin_user
            assert (
                database_config_current.password
                != documentdb_config_current.admin_password
            )

    for (database_config_current, database_config_different) in itertools.combinations(
        database_configs, 2
    ):
        assert database_config_current.user != database_config_different.user
        assert database_config_current.password != database_config_different.password
