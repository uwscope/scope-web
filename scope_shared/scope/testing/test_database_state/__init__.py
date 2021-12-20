"""
Import all tests that should be executed to check database state.

Packages can then import this single module for their own check of database state.
"""

from scope.testing.test_database_state.test_patients_collection import *
