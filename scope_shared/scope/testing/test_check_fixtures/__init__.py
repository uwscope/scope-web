"""
Import all tests that should be executed to check fixtures.

Packages can then import this single module for their own check of fixtures.
"""

from scope.testing.test_check_fixtures.test_check_fixtures_database import *
from scope.testing.test_check_fixtures.test_check_fixtures_documentdb import *
from scope.testing.test_check_fixtures.test_check_fixtures_flask import *
