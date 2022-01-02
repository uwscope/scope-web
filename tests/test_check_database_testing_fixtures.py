"""
This module checks the fixtures that support many other tests.
Many fixtures xfail if a condition is not met, preventing verbose output of many tests failing.
This module sets TESTING_CHECK_FIXTURES so such fixtures can know they are being tested.
Fixtures should then fail and therefore allow inspection of the failure.
"""

import tests.testing_config

TESTING_CONFIGS = tests.testing_config.DATABASE_TESTING_CONFIGS
TESTING_CHECK_FIXTURES = True

from scope.testing.test_check_fixtures import *
