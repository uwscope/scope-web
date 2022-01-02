import tests.testing_config

TESTING_CONFIGS = tests.testing_config.DATABASE_TESTING_CONFIGS
UNIQUE_DOCUMENTDB_CONFIGS = tests.testing_config.UNIQUE_DOCUMENTDB_CONFIGS
UNIQUE_DATABASE_CONFIGS = tests.testing_config.UNIQUE_DATABASE_CONFIGS

from scope.testing.test_database_state import *
