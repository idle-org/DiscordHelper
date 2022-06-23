import sys
import importlib
import threading
import time
import queue
from collections import deque
from modules.internal_io import global_status, test_status, return_code_dict

"""
All modules that can be tested
Associate the arguments passed to the command line with the modules to be loaded
argparse argument : [module_name, class_name]
"""
_TEST_MODULES = {
    "spidey": ["spidey_test", "SpideyTest"],
}
POST_RUN_ALLOWED = False


class TestRunner:
    def __init__(self, args, agnpath):
        """
        Main spidey runner
        :param args: List of arguments
        :type args: argparse.Namespace
        :param agnpath: The path to the discord folder
        :type agnpath: agnostic_path.AgnosticPath
        """
        self.ptb = args.ptb
        self.args = args
        self.agnostic_path = agnpath
        self.os_name = agnpath.os
        self.main_path = agnpath.main_path
        self.version = agnpath.version

        self.is_infected = 0
        self.detections = 0
        self.test_run = {}

        self.loaded_test_modules = {}
        self.loaded_test_classes = {}
        self.list_of_tests = []
        self.update_module_list()

        self.finished_tests = deque()

        self.exec_all_tests()

    def update_module_list(self):
        """
        Gets the list of modules to be loaded (in accordance to the config)
        :return: List of modules
        :rtype: list
        """
        modules = {}
        classes = {}
        module_name = None
        try:
            for module_name, values in _TEST_MODULES.items():
                if self.args.__getattribute__(module_name):
                    modules[values[0]] = importlib.import_module(f"modules.{values[0]}")
                    classes[values[0]] = getattr(modules[values[0]], values[1])

        except AttributeError:
            print(f"The module {module_name} was not loaded because it was not specified in the config.")

        self.loaded_test_modules.update(modules)
        self.loaded_test_classes.update(classes)

    def exec_all_tests(self):
        """
        Executes all the tests, get their result as they finishes
        :return: The number of test ran, success, failures, skipped (with ran = success+failures+skip)
        :rtype: (int,int,int,int) # TODO: Change this to a nametuple
        """
        self.list_of_tests = []
        for module_name, test_class in self.loaded_test_classes.items():
            for i in range(10):
                print(f"Starting test {module_name}")
                tc = test_class(self.args, self.agnostic_path, None, self.finished_tests)
                tc = threading.Thread(target=tc.run_test, args=())
                tc.name = str(module_name)
                tc.daemon = True
                self.list_of_tests.append(tc)
                tc.start()

        # Launch a controller to allow the user to stop all tests
        # controller = threading.Thread(target=self.test_launcher)
        # Allow the user to stop the tests
        tc = threading.Thread(target=self.controller_test, args=())
        tc.daemon = True
        tc.start()

        # Await the end of the tests or the user interruption
        tc = threading.Thread(target=self.post_test_runner, args=())
        tc.start()

        # Wait for the end of the tests
        tc = threading.Thread(target=self.test_waiter, args=())
        tc.daemon = True
        tc.start()

        return self.is_infected, self.detections, self.test_run

    def controller_test(self):
        """
        Kills the tests if the user press enter
        """
        print("Press enter to stop the tests: ")
        while True:
            if input() == "":
                if not self.is_infected:
                    global POST_RUN_ALLOWED
                    POST_RUN_ALLOWED = True
                return

    def post_test_runner(self):
        """
        Runs the post test runner if all tests are finished
        """
        global POST_RUN_ALLOWED
        if self.args.launch:
            while True:
                if POST_RUN_ALLOWED:
                    print("Running post test runner")
                    return 0
                time.sleep(0.5)
        return 0

    def test_waiter(self):
        """
        Waits for the end of the tests
        :return:
        """
        for t in self.list_of_tests:  # Can only proceed if all tests are finished
            t.join()

        # When all tests are finished or the user stopped the tests, we can proceed
        if not self.is_infected:
            global POST_RUN_ALLOWED
            POST_RUN_ALLOWED = True

    def get_exit_code(self):
        """
        Gets the exit code of the tests
        :return: The exit code
        :rtype: int
        """
        global POST_RUN_ALLOWED
        if POST_RUN_ALLOWED:
            for t in self.list_of_tests:
                if t.is_alive():
                    return 2  # 2 means that the user stopped the tests before the end
            return self.is_infected  # The user didn't stop the tests

        return -1  # The program is not finished yet

    def get_status(self):
        """
        Gets the status of the tests
        :return: The status
        :rtype: str
        """
        nb_tests = len(self.list_of_tests)
        nb_tests_success = 0
        nb_tests_failure = 0
        nb_tests_skipped = 0
        for test in self.finished_tests:
            print(f"Test {test.name} finished with status {test.status}")
            if test.status == 0:
                nb_tests_success += 1
            elif test.status == 1:
                nb_tests_failure += 1
            elif test.status == 2:
                nb_tests_skipped += 1

        nb_tests_ran = nb_tests_success + nb_tests_failure + nb_tests_skipped
        nb_test_running = nb_tests - nb_tests_ran
        return global_status(
            total_tests=nb_test_running,
            tests_finished=nb_tests_ran,
            tests_failed=nb_tests_failure,
            tests_running=nb_test_running,
            tests_skipped=nb_tests_skipped,
        )


def run_check(args, agnpath):
    """
    Runs all operations selected in the config
    :param args: List of arguments
    :param agnpath: Annostic path to the discord folder
    :return: None
    """
    tr = TestRunner(args, agnpath)  # All operation are executed in parallel and the user can stop them

    print("Waiting for the end of the tests")
    while tr.get_exit_code() == -1:
        print(tr.get_status())
        time.sleep(0.5)

    sys.exit(tr.get_exit_code())
