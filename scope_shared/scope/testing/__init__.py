from scope.testing.testing_config import TestingConfig
from scope.testing.testing_check_fixtures import testing_check_fixtures

PYTEST_PLUGINS = [
    "scope.testing.fixtures_config",
    "scope.testing.fixtures_database",
    "scope.testing.fixtures_documentdb",
    "scope.testing.fixtures_flask",
    "scope.testing.data.fixtures_fake_patient",
]
