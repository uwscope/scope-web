from scope.testing.testing_config import TestingConfig


PYTEST_PLUGINS = [
    "scope.testing.fixtures_config",
    "scope.testing.fixtures_documentdb",
    "scope.testing.fixtures_flask",
    "scope.testing.fixtures_testing",
]
