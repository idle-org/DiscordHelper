"""
Internal interfacting objects.
"""

from collections import namedtuple


global_status = namedtuple('global_status', 'total_tests, tests_finished, tests_failed, tests_running, tests_skipped', defaults=(0, 0, 0, 0, 0))
test_status = namedtuple('test_status', 'name, status, message', defaults=(None, None, None))
return_code_dict = {
    2: "The test was not run",
    3: "The test is running",
    0: "The test is a success",
    1: "Test has failed",
    4: "Test found problems",
}

