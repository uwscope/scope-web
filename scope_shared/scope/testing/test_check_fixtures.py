"""
Import all tests that should be executed to check all fixtures.

Packages can then import this single module for their own check fixtures.
"""

from scope.testing.test_check_fixtures_database import *
from scope.testing.test_check_fixtures_documentdb import *
from scope.testing.test_check_fixtures_flask import *
