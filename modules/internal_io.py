"""
Internal interfacting objects.
"""

from collections import namedtuple


global_status = namedtuple(
    'global_status',
    'tests_total, tests_finished, tests_success, tests_failed, tests_running, tests_skipped, tests_error, progress',
    defaults=(0, 0, 0, 0, 0, 0, 0, 0)
)
test_status = namedtuple(
    'test_status', 'name, status, message, failure_dict, data, progress',
    defaults=(None, None, None, {}, {}, 0)
)
return_code_dict = {
    "skipped": "The test was not run",
    "running": "The test is running",
    "success": "The test is a success",
    "failure": "Test has failed",
    "problems": "Test found problems",
    "idle": "Test is idle",
}
