"""
Import all tests that should be executed to check database assumptions about database semantics.

Packages can then import this single module.
"""

from scope.testing.test_documentdb_semantics.test_index import *
from scope.testing.test_documentdb_semantics.test_query import *
