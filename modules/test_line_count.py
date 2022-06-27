"""
Test against the line count of the files in the discord folder.
"""

from modules import test_template, internal_io


class LineCount(test_template.TestWalkTemplateSimpleFunction):
    def __init__(self, thread_parameters: internal_io.thread_parameters):
        """
        Simple test runner, compare line count to known good values.
        """
        super().__init__(thread_parameters, lambda path: len(open(path, "rb").readlines()), " lines")
