import os

from modules import test_template


class SizeCheck(test_template.TestWalkTemplateSimpleFunction):
    def __init__(self, thread_parameters):
        """
        Simple test runner, compare file size to known good values.
        """
        super().__init__(thread_parameters, os.path.getsize, " bytes")
