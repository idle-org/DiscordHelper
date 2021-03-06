"""
A global template for all tests.
"""
import os
from typing import Callable, Union

from modules import internal_io, agnostic_paths


class TestDataError(Exception):
    """
    Raised when the data is not valid.
    """
    pass


class TestTemplate:
    def __init__(self, thread_parameters: internal_io.thread_parameters, use_cache: bool = True) -> None:
        """
        Simple test template.
        :param thread_parameters.args: List of arguments
        :type thread_parameters.args: argparse.Namespace
        :param thread_parameters.agnpath: The path to the discord folder
        :type thread_parameters.agnpath: agnostic_path.AgnosticPath
        :param thread_parameters.test_data: The data to be tested
        :type thread_parameters.test_data: dict
        :param thread_parameters.queue: The queue to put the test status in
        :type thread_parameters.queue: queue.deque
        :param thread_parameters.queue_lock: The lock to use when putting the test status in the queue
        :type thread_parameters.queue_lock: threading.Lock
        :param thread_parameters.dict_process: The dictionary of processes
        :type thread_parameters.dict_process: dict
        :param thread_parameters.dict_process_lock: The lock to use when putting the process in the dictionary
        :type thread_parameters.dict_process_lock: threading.Lock
        :param thread_parameters.bad_database: Whether the database was sucessfully loaded and contains valid data
        :type thread_parameters.bad_database: bool
        """
        self.args = thread_parameters.args
        self.ptb = thread_parameters.args.ptb
        self.agnostic_path = thread_parameters.agnpath
        self.os_name = thread_parameters.agnpath.os
        self.main_path = thread_parameters.agnpath.main_path
        self.test_data = thread_parameters.test_data
        self.is_infected = False
        self.status_code = "idle"
        self.status = "Test not yet initialized."
        self.queue = thread_parameters.queue
        self.set_status("idle")
        self.queue_lock = thread_parameters.queue_lock
        self.failure_dict = {}
        self.new_data = {}
        self.progress = 0
        self.use_cache = use_cache
        self.is_unknown = False
        self.dict_process = thread_parameters.dict_process
        self.dict_process_lock = thread_parameters.dict_process_lock
        self.bad_database = thread_parameters.bad_database
        self.dict_process_lock.acquire()
        self.dict_process[self.name()] = self
        self.dict_process_lock.release()
        self.init_test_data()

    def run(self) -> None:
        """
        Runs the test.
        """
        try:
            self.run_test()
        except Exception as e:
            self.add_failure("problem", "DISCORD HELPER:" + str(e))
            return self.finish("problem", str(e))

    def run_test(self) -> None:
        """
        The main runner function, must be implemented by the child class.
        During the execution of the test, the status code and status MUST be updated.
        """
        self.set_status("running", "The test will begin shortly, please wait...")
        self.set_status("sucess", "The test was a success but kinda not a success.")

    def init_test_data(self) -> Union[str, None]:
        if self.test_data is None and not self.args.continue_on_error:
            self.set_status("problem", "No test data given.")
            return self.finish()

    def name(self) -> str:
        """
        :return: Name of the test
        """
        return str(self.__class__.__name__)

    def get_status_code(self) -> str:
        """
        :return: Status code at the time of call.
        """
        return self.status_code

    def get_status(self) -> internal_io.test_status:
        """
        :return: Status at the time of call.
        """
        return internal_io.test_status(
            name=self.name(),
            status=self.status_code,
            message=self.status,
            failure_dict=self.failure_dict,
            data=self.new_data,
            progress=self.progress,
        )

    @staticmethod
    def get_status_from_code(code: str) -> str:
        """
        :param code: The status code to get the status from.
        :return: Description of the status code
        """
        return internal_io.return_code_dict[code]

    def set_status(self, statuscode: str, message: str = None) -> str:
        """
        Sets a new status code.
        :param statuscode: Status code to set
        :param message: Message to set
        :return: new status code
        """
        self.status_code = statuscode
        if message is not None:
            self.status = message
        else:
            self.status = self.get_status_from_code(statuscode)
        return self.status_code

    def finish(self, statuscode: str = None, message: str = None) -> str:
        """
        Finishes the test.
        :param statuscode: Status code to set
        :param message: Message to set
        :type statuscode: str
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

    def add_failure(self, path: str, message: str) -> None:
        """
        Adds a failure to the failure dictionary.
        :param path: Path to the file that failed
        :param message: Message to add
        """
        self.failure_dict[path] = message

    def __del__(self) -> None:
        """
        Destructor.
        """
        if self.status_code == "running":
            return self.finish("skipped")

    def add_to_new_data(self, entry: str, testname: str, value: str) -> any:
        """
        Adds a new entry to the database.
        :param entry: The entry to add
        :param testname: The name of the test
        :param value: The value of the entry
        :return: The value of the entry
        """
        if entry not in self.new_data:
            self.new_data[entry] = {}
        self.new_data[entry][testname] = value
        return value

    def get_from_new_data(self, entry: str, testname: str) -> any:
        """
        Gets the value of an entry from the database.
        :param entry: The entry to get
        :param testname: The name of the test
        :return: The value of the entry
        """
        if entry in self.new_data:
            if testname in self.new_data[entry]:
                return self.new_data[entry][testname]
        return None

    def get_from_database(self, entry: str, testname: str) -> any:
        """
        Gets the value of an entry from the database.
        :param entry: The entry to get
        :param testname: The name of the test
        :return: The value of the entry
        """
        if self.test_data:
            if "tests" in self.test_data:
                if entry in self.test_data["tests"]:
                    if testname in self.test_data["tests"][entry]:
                        return self.test_data["tests"][entry][testname]
        return None


class TestWalkTemplate(TestTemplate):
    def __init__(self, thread_parameters: internal_io.thread_parameters, use_cache: bool = False):
        """
        Simple test template.
        """
        super().__init__(thread_parameters, use_cache)
        self.to_skip = []

    def run_test(self) -> str:
        """
        The main runner function, must be implemented by the child class.
        Here is an example of how to use the add_test_result function.
        """
        self.set_status("running", "The test will begin shortly, please wait...")

        for path in self.walk():
            if not self.compare(path, "test", lambda x: True, [], {}):
                self.add_failure(path, f"Test {self.name()} failed on {path}")
                if not self.args.continue_on_error:
                    self.set_status("failure", f"Test {self.name()} failed on {path}")
                    return self.finish()

        if len(self.failure_dict) > 0:
            if self.bad_database:
                self.set_status("unknown", f"Test {self.name()} failed on {len(self.failure_dict)} files")
            else:
                self.set_status("failure", f"Test {self.name()} failed on {len(self.failure_dict)} files.")
        else:
            self.set_status("success", f"Test {self.name()} passed.")

        return self.finish()

    def walk(self) -> list:
        """
        Walks the given path and returns a list of all files and directories.
        :return: List of all files
        """
        return self.agnostic_path.all_files

    def add_test_result(self, path: str, testname: str, result: any) -> any:
        """
        Adds a test result to the data dictionary.
        :param path: Path to the file being tested
        :param testname: Name of the test
        :param result: Result of the test
        :return: The result of the test
        """
        path = self.agnostic_path.get_short_path(path)
        return self.add_to_new_data(path, testname, result)

    def get_test_data(self, path: str, testname: str) -> any:
        """
        Gets the test data from the data dictionary.
        :param path: Path to the file being tested
        :param testname: Name of the test
        """
        return self.get_from_new_data(self.agnostic_path.get_short_path(path), testname)

    def get_expected_result(self, path: str, testname: str) -> Union[str, None]:
        """
        Gets the expected result from the data dictionary.
        :param path: Path to the file being tested
        :param testname: Name of the test
        """
        if self.test_data:
            return self.get_from_database(self.agnostic_path.get_short_path(path), testname)
        return None

    def compare(self, path: agnostic_paths.AgnosticPaths, entry_name: str, function: Callable,
                args: list, kwargs: dict, cmp_function: Callable = None):
        """
        Use the function on the given path, with given arguments and compare it with the entry in the test data.
        :param path: Path to the file or directory
        :param entry_name: Name of the entry in the test data
        :param function: Function to use on the path
        :param args: Arguments to use on the function
        :param kwargs: Keyword arguments to use on the function
        :param cmp_function: Function compare both results
        """

        if self.agnostic_path.get_short_path(path) in self.to_skip:
            return True
        if self.use_cache:
            kwargs["cached_data"] = self.agnostic_path.cached_file(path)
        else:
            kwargs["cached_data"] = None
        data_origin = self.add_test_result(path, entry_name, function(path, *args, **kwargs))

        expected_data = self.get_expected_result(path, entry_name)
        if expected_data is None and not self.args.continue_on_error:
            self.set_status("problem", f"No expected data found for {path}")
            return False

        if cmp_function is None:
            if data_origin == expected_data:
                return True
            return False
        else:
            if cmp_function(data_origin, expected_data):
                return True
            return False


class TestWalkTemplateNoLogs(TestWalkTemplate):
    def __init__(self, thread_parameters: internal_io.thread_parameters, use_cache: bool = False):
        """
        Simple test template.
        """
        super().__init__(thread_parameters, use_cache)
        self.to_skip = [r"modules\discord_dispatch-1\discord_dispatch\dispatch.log"]


class TestWalkTemplateSimpleFunction(TestWalkTemplateNoLogs):
    def __init__(self, thread_parameters: internal_io.thread_parameters,
                 function: Callable, unit_test: str, use_cache: bool = False):
        """
        A test template that runs a simple function on every file, and compares the result with the expected data.
        :param thread_parameters: Thread parameters
        :param function: Function to use on every file
        :param unit_test: A descriptor of what the test returns
        """
        super().__init__(thread_parameters, use_cache)
        self.function = function
        self.test_name = self.name()
        self.unit_test = unit_test

    def run_test(self) -> bool:
        """
        Walk all files and check their size.
        :return: Whether any of the files are larger than the expected size.
        """
        self.set_status("running")
        size = self.agnostic_path.size

        error_msg = ""
        for i, path in enumerate(self.walk()):
            self.progress = int(100*i / size)
            short_path = self.agnostic_path.get_short_path(path)
            if os.path.isfile(path):
                if not self.compare(path, self.test_name, self.function, (), {}):
                    res = self.get_test_data(path, self.test_name)
                    self.add_failure(path, f"Test {self.name()} failed on {short_path}")
                    error_msg += f"{short_path} is " \
                                 f"({res}{self.unit_test}) not ({self.get_expected_result(path, self.test_name)}" \
                                 f"{self.unit_test}).\n"
                    # print(self.bad_database)
                    if not self.bad_database:
                        self.is_infected = True
                        if not self.args.continue_on_error:
                            return self.finish(
                                "failure",
                                f"{short_path} is supposed to be {self.get_expected_result(path, self.test_name)}"
                                f" {self.unit_test}, but it is {self.get_expected_result(path, self.test_name)}"
                                f"{self.unit_test}.")
                    else:
                        self.is_unknown = True
                        if not self.args.continue_on_error:
                            return self.finish(
                                "problem",
                                f"{short_path} is supposed to be {self.get_expected_result(path, self.test_name)}"
                                f"{self.unit_test}, but it is {os.path.getsize(path)}{self.unit_test}")

        self.progress = 100
        if self.is_infected:
            return self.finish(
                "failure",
                error_msg
            )
        elif self.is_unknown:
            return self.finish(
                "problem",
                error_msg
            )
        return self.finish("success", "Your discord is not infected.")
