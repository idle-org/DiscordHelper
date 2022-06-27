"""
Fast adler32 checksum implementation.
"""

from modules import test_template, internal_io
from zlib import adler32


def apply_adler(path: str) -> hex:
    """
    Apply the adler32 checksum to a file.
    :param path: The path to the file.
    :return: The adler32 checksum.
    """
    with open(path, "rb") as f:
        return hex(adler32(f.read()))


class Adler32(test_template.TestWalkTemplateSimpleFunction):
    def __init__(self, thread_parameters: internal_io.thread_parameters):
        """
        Simple test runner, compare adler32 to known good values.
        """
        super().__init__(thread_parameters, apply_adler, "")
