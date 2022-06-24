"""
A global template for all tests.
"""

from modules import internal_io


class TestDataError(Exception):
    """
    Raised when the data is not valid.
    """
    pass


class TestTemplate:
    def __init__(self, args, agnpath, test_data, queue, queue_lock):
        """
        Simple test template.
        :param args: List of arguments
        :type args: argparse.Namespace
        :param agnpath: The path to the discord folder
        :type agnpath: agnostic_path.AgnosticPath
        :param test_data: The data to be tested
        :type test_data: str
        :param queue: The queue to put the test status in
        :type queue: queue.deque
        :param queue_lock: The lock to use when putting the test status in the queue
        :type queue_lock: threading.Lock
        """
        self.args = args
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
        self.queue_lock = queue_lock
        self.failure_dict = {}
        self.new_data = {}
        self.progress = 0

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
        return internal_io.test_status(
            self.name(),
            self.status_code,
            self.status,
            self.failure_dict,
            self.new_data,
            self.progress
        )

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

    def finish(self, statuscode: str = None, message: str = None):
        """
        Finishes the test.
        """
        if message is not None:
            self.status = message
        if statuscode is not None:
            self.status_code = statuscode

        self.queue_lock.acquire()
        # self.progress = 1
        self.queue.append(self.get_status())
        self.queue_lock.release()
        return self.get_status_code()

    def add_failure(self, path, message):
        """
        Adds a failure to the failure dictionary.
        :param path: Path to the file that failed
        :type path: str
        :param message: Message to add
        :type message: str
        """
        self.failure_dict[path] = message

    def __del__(self):
        """
        Destructor.
        """
        if self.status_code == "running":
            return self.finish("skipped")


class TestWalkTemplate(TestTemplate):
    def __init__(self, args, agnpath, test_data, queue, queue_lock):
        """
        Simple test template.
        :param args: List of arguments
        :type args: argparse.Namespace
        :param agnpath: The path to the discord folder
        :type agnpath: agnostic_path.AgnosticPath
        :param test_data: The data to be tested
        :type test_data: str
        """
        super().__init__(args, agnpath, test_data, queue, queue_lock)
        if test_data is None:
            self.set_status("problem", "No test data given.")

    def add_test_result(self, path, testname, result):
        """
        Adds a test result to the data dictionary.
        :param path: Path to the file that was tested
        :type path: str
        :param testname: Name of the test
        :type testname: str
        :param result: Result of the test
        :type result: any
        """

        if path not in self.new_data:
            self.new_data[path] = {}
        self.new_data[path][testname] = result
        return result

    def get_test_data(self, path, testname):
        """
        Gets the test data from the data dictionary.
        :param path: Path to the file that was tested
        :type path: str
        :param testname: Name of the test
        :type testname: str
        :return: Test data
        :rtype: any
        """
        if path in self.new_data:
            if testname in self.new_data[path]:
                return self.new_data[path][testname]
        return None

    def get_expected_result(self, path, testname):
        """
        Gets the expected result from the data dictionary.
        :param path: Path to the file that was tested
        :type path: str
        :param testname: Name of the test
        :type testname: str
        :return: Expected result
        :rtype: any
        """
        if self.test_data:
            if path in self.test_data:
                if testname in self.test_data[path]:
                    return self.test_data[path][testname]
        return None

    def run_test(self):
        """
        The main runner function, must be implemented by the child class.
        Here is an example of how to use the add_test_result function.
        :return:
        """
        self.set_status("running", "The test will begin shortly, please wait...")

        if self.test_data is None and not self.args.continue_on_error:
            self.set_status("problem", "No test data given.")
            return self.finish()

        self.set_status("running", "The test will begin shortly, please wait...")
        for path in self.walk():
            print(path)
            if not self.compare(path, "test", lambda x: True, [], {}):
                self.add_failure(path, f"Test {self.name()} failed on {path}")
                if not self.args.continue_on_error:
                    self.set_status("failure", f"Test {self.name()} failed on {path}")
                    return self.finish()

        if len(self.failure_dict) > 0:
            self.set_status("failure", f"Test {self.name()} failed on {len(self.failure_dict)} files.")
        else:
            self.set_status("success", f"Test {self.name()} passed.")

        return self.finish()

    def walk(self):
        """
        Walks the given path and returns a list of all files and directories.
        :return: List of all files and directories
        :return:
        """
        return self.agnostic_path.walk_all_files(self.agnostic_path())

    def compare(self, path, entry_name, function, args, kwargs):
        """
        Use the function on the given path, with given arguments and compare it with the entry in the test data.
        :param path: Path to the file or directory
        :type path: agnostic_path.AgnosticPath
        :param entry_name: Name of the entry in the test data
        :type entry_name: str
        :param function: Function to use on the path
        :type function: function
        :param args: Arguments to use on the function
        :type args: list
        :param kwargs: Keyword arguments to use on the function
        :type kwargs: dict
        """

        data_origin = self.add_test_result(path, entry_name, function(path, *args, **kwargs))
        expected_data = self.get_expected_result(path, entry_name)
        if expected_data is None and not self.args.continue_on_error:
            self.set_status("problem", f"No expected data found for {path}")
            return False

        if data_origin != expected_data:
            return False
        return True

