from scope.testing.testing_check_fixtures import testing_check_fixtures
from scope.testing.testing_config import TestingConfig

PYTEST_PLUGINS = [
    "scope.testing.fake_data.fixtures_fake_patient_profile",
    "scope.testing.fake_data.fixtures_fake_contact",
    "scope.testing.fake_data.fixtures_fake_safety_plan",
    "scope.testing.fake_data.fixtures_fake_clinical_history",
    "scope.testing.fake_data.fixtures_fake_values_inventory",
    "scope.testing.fake_data.fixtures_fake_life_areas",
    "scope.testing.fixtures_config",
    "scope.testing.fixtures_database",
    "scope.testing.fixtures_database_temp_collection",
    "scope.testing.fixtures_database_temp_patient",
    "scope.testing.fixtures_documentdb",
    "scope.testing.fixtures_faker",
    "scope.testing.fixtures_flask",
]
