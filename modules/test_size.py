import os

from modules import test_template, internal_io


def get_size(path: str, cached_data: bytes = None) -> int:  # noqa: E501
    """
    Get the size of a file.
    :param path: The path to the file.
    :return: The size of the file.
    """
    return os.path.getsize(path)


class SizeCheck(test_template.TestWalkTemplateSimpleFunction):
    def __init__(self, thread_parameters: internal_io.thread_parameters):
        """
        Simple test runner, compare file size to known good values.
        """
        super().__init__(thread_parameters, get_size, " bytes", use_cache=False)
