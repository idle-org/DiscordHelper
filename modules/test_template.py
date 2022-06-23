"""
A global template for all tests.
"""

from modules import internal_io


class TestTemplate:
    def __init__(self, args, agnpath, test_data, queue):
        """
        Simple test template.
        :param args: List of arguments
        :type args: argparse.Namespace
        :param agnpath: The path to the discord folder
        :type agnpath: agnostic_path.AgnosticPath
        :param test_data: The data to be tested
        :type test_data: str
        """
        self.ptb = args.ptb
        self.agnostic_path = agnpath
        self.os_name = agnpath.os
        self.main_path = agnpath.main_path
        self.test_data = test_data
        self.is_infected = False
        self.status_code = 0
        self.status = "Test not yet initialized."
        self.queue = queue

    def name(self):
        """
        :return: Name of the test
        :rtype: str
        """
        return str(self.__class__.__name__)

    def get_status_code(self):
        """
        :return: Status code at the time of call.
        :rtype: int
        """
        return self.status_code

    def get_status(self):
        """
        :return: Status at the time of call.
        :rtype: str
        """
        return internal_io.test_status(self.name(), self.status_code, self.status)

    @staticmethod
    def get_status_from_code(code):
        """
        :return: Description of the status code
        :rtype: str
        """
        return internal_io.return_code_dict[code]

    def set_status(self, statuscode: int):
        """
        Sets a new status code.
        :param statuscode: Status code to set
        :type statuscode: int
        :return: new status code
        :rtype: int
        """
        self.status_code = statuscode
        self.status = self.get_status_from_code(statuscode)
        return self.status_code
