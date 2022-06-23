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
        self.status_code = "idle"
        self.status = "Test not yet initialized."
        self.queue = queue
        self.set_status("idle")

    def run_test(self):
        """
        The main runner function, must be implemented by the child class.
        During the execution of the test, the status code and status MUST be updated.
        """
        self.set_status("running", "The test will begin shortly, please wait...")
        self.set_status("sucess", "The test was a success but kinda not a success.")

    def name(self):
        """
        :return: Name of the test
        :rtype: str
        """
        return str(self.__class__.__name__)

    def get_status_code(self):
        """
        :return: Status code at the time of call.
        :rtype: str
        """
        return self.status_code

    def get_status(self):
        """
        :return: Status at the time of call.
        :rtype: internal_io.test_status
        """
        return internal_io.test_status(self.name(), self.status_code, self.status)

    @staticmethod
    def get_status_from_code(code):
        """
        :param code: The status code to get the status from.
        :type code: str
        :return: Description of the status code
        :rtype: str
        """
        return internal_io.return_code_dict[code]

    def set_status(self, statuscode: str, message: str = None):
        """
        Sets a new status code.
        :param statuscode: Status code to set
        :param message: Message to set
        :type statuscode: str
        :return: new status code
        :rtype: str
        """
        self.status_code = statuscode
        if message is not None:
            self.status = message
        else:
            self.status = self.get_status_from_code(statuscode)
        return self.status_code
