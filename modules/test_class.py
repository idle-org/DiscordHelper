class Test:
    def __init__(self, args, agnpath, test_data):
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
        self.return_code_dict = {
            0: "The test was not run",
            1: "The test is running",
            2: "The test is a success",
            3: "Test has failed",
            4: "Test found problems",
        }

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
        return self.status

    def get_status_from_code(self):
        """
        :return: Description of the status code
        :rtype: str
        """
        return self.return_code_dict[self.status_code]

    def set_status(self, statuscode: int):
        """
        Sets a new status code.
        :param statuscode: Status code to set
        :type statuscode: int
        :return: new status code
        :rtype: int
        """
        self.status_code = statuscode
        return self.status_code
