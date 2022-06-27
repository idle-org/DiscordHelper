"""
Fast adler32 checksum implementation.
"""

from modules import test_template
from zlib import adler32


def apply_adler(path):
    """
    Apply the adler32 checksum to a file.
    :param path: The path to the file.
    :type path: str
    :return: The adler32 checksum.
    :rtype: int
    """
    with open(path, "rb") as f:
        return hex(adler32(f.read()))


class Adler32(test_template.TestWalkTemplateSimpleFunction):
    def __init__(self, thread_parameters):
        """
        Simple test runner, compare adler32 to known good values.
        """
        super().__init__(thread_parameters, apply_adler, "")
