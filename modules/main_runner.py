import json
import os
import sys
import importlib
import threading
import time
from collections import deque
from modules.internal_io import global_status  # , test_status, return_code_dict

"""
All modules that can be tested
Associate the arguments passed to the command line with the modules to be loaded
argparse argument : [module_name, class_name]
"""
_TEST_MODULES = {
    "spidey": ["spidey_test", "SpideyTest"],
    # "test_walk": ["test_template", "TestWalkTemplate"],
}

PROGRAM_VERSION = "1.0.0"
POST_RUN_ALLOWED = False

queue_lock = threading.Lock()


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
                if self.args.all or self.args.__getattribute__(module_name):
                    modules[values[0]] = importlib.import_module(f"modules.{values[0]}")
                    classes[values[0]] = getattr(modules[values[0]], values[1])

        except AttributeError as e:
            print(f"The module {module_name} was not loaded because it was not specified in the config.")
            print(e)

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
            print(f"Starting test {module_name}")
            tc = test_class(self.args, self.agnostic_path, None, self.finished_tests, queue_lock)
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
                    print("Running post test runner...")
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
        queue_lock.acquire()
        nb_tests = len(self.list_of_tests)
        nb_tests_success = 0
        nb_tests_failure = 0
        nb_tests_skipped = 0
        for test in self.finished_tests:
            print(f"Test {test.name} finished with status {test.status}")
            if test.status == "success":
                nb_tests_success += 1
            elif test.status == "failure":
                nb_tests_failure += 1
            elif test.status == "skipped":
                nb_tests_skipped += 1
            elif test.status == "problem":
                nb_tests_failure += 1
        queue_lock.release()
        nb_tests_ran = nb_tests_success + nb_tests_failure + nb_tests_skipped
        nb_test_running = nb_tests - nb_tests_ran
        return global_status(
            tests_total=nb_tests,
            tests_finished=nb_tests_ran,
            test_success=nb_tests_success,
            tests_failed=nb_tests_failure,
            tests_running=nb_test_running,
            tests_skipped=nb_tests_skipped,
            tests_error=nb_tests_failure
        )

    def get_test_data(self):
        """
        Gets the test data
        :return: The test data
        :rtype: dict
        """
        data = {}
        queue_lock.acquire()
        for test in self.finished_tests:
            for key, value in test.data.items():
                if key not in data:
                    data[key] = value
                else:
                    data[key].update(value)
            # data.update(test.data)
        queue_lock.release()
        return data


def export_data(test_runner, data):
    """
    Exports the test data
    :param test_runner: The test runner
    :type test_runner: TestRunner
    :param data: The test data
    :type data: dict
    """
    main_data = {
        "global":
            {
                "os": test_runner.os_name,
                "ptb": test_runner.ptb,
                "discord_version": test_runner.version,
                "program_version": PROGRAM_VERSION,
            },
        "tests": data,
    }
    return main_data


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
        print(tr.get_status())  # TODO : Print status in a more readable way
        time.sleep(0.5)
    print("The test sequence is now finished")

    print(tr.get_status())  # TODO: Print the final status, test still running are actually skipped
    if args.gen_data:
        print("Generating data...")
        data = tr.get_test_data()
        print("Making folder...")
        file_path = os.path.join(os.path.join("databases", args.gen_data[0]))
        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            os.makedirs(args.gen_data)
        print("Exporting data...")
        main_data = export_data(tr, data)
        # print(main_data)
        with open(file_path, "w") as f:
            json.dump(main_data, f, indent=4)
        # print(tr.get_test_data())  # TODO: Transorm the data into a yaml or json file

    print(f"Exiting in {args.timeout}...")
    time.sleep(args.timeout)
    sys.exit(tr.get_exit_code())
