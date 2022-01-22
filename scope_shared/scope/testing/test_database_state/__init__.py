"""
Import all tests that should be executed to check database state.

Packages can then import this single module.
"""

from scope.testing.test_database_state.test_patients_collection import *
from scope.testing.test_database_state.test_unique_credentials import *
