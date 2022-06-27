import argparse
import json
import os
import subprocess
import sys
import importlib
import threading
import time
from collections import deque
from typing import List

from modules.internal_io import global_status, thread_parameters
from modules import agnostic_paths, internal_io

"""
All modules that can be tested
Associate the arguments passed to the command line with the modules to be loaded
argparse argument : [module_name, class_name]
"""
from termcolor import colored
os.system('color')
# red, green, yellow, blue, magenta, cyan, white.

_TEST_MODULES = {
    "spidey": ["test_spidey", "SpideyTest"],
    "file_size": ["test_size", "SizeCheck"],
    "adler": ["test_adler", "Adler32"],
    "file_hash": ["test_sha", "Sha256"],
    "line_count": ["test_line_count", "LineCount"],
}

PROGRAM_VERSION = "1.0.0"
POST_RUN_ALLOWED = False  # TODO : Remove this line, only use is_infected
RUN_OVER = False

queue_lock = threading.Lock()
processes_lock = threading.Lock()

CLEAR_CODE = colored(r"""
 _______ _
(_______) |
 _      | | _____ _____  ____
| |     | || ___ (____ |/ ___)
| |_____| || ____/ ___ | |
 \______)\_)_____)_____|_|
 """, 'green')

INFECTED_CODE = colored(r"""
 _         ___                             _
| |       / __)              _            | |
| |____ _| |__ _____  ____ _| |_ _____  __| |
| |  _ (_   __) ___ |/ ___|_   _) ___ |/ _  |
| | | | || |  | ____( (___  | |_| ____( (_| |
|_|_| |_||_|  |_____)\____)  \__)_____)\____|
""", 'red')

UNKNOWN_CODE = colored(r"""
 _     _       _
(_)   (_)     | |
 _     _ ____ | |  _ ____   ___  _ _ _ ____
| |   | |  _ \| |_/ )  _ \ / _ \| | | |  _ \
| |___| | | | |  _ (| | | | |_| | | | | | | |
 \_____/|_| |_|_| \_)_| |_|\___/ \___/|_| |_|
""", 'yellow')

LOGO = colored(r"""
  __ \  _)                              |  |   |        |
  |   |  |   __|   __|   _ \    __|  _` |  |   |   _ \  |  __ \    _ \   __|
  |   |  | \__ \  (     (   |  |    (   |  ___ |   __/  |  |   |   __/  |
 ____/  _| ____/ \___| \___/  _|   \__,_| _|  _| \___| _|  .__/  \___| _|
                                                          _|
""", "cyan")


class TestRunner:
    def __init__(self, args: argparse.Namespace, agnpath: agnostic_paths.AgnosticPaths, start_time: float):
        """
        Main spidey runner
        :param args: List of arguments
        :param agnpath: The path to the discord folder
        :param start_time: The time the test started
        """
        self.ptb = args.ptb
        self.args = args
        self.agnostic_path = agnpath
        self.os_name = agnpath.os
        self.main_path = agnpath.main_path
        self.version = agnpath.version
        self.start_time = start_time
        self.selected_tests = []

        self.is_infected = 0  # Only set to 1 if the certainty is high enough
        self.is_unknown = 1  # Unknown if the file is infected or not
        self.threat_level = 0  # The threat level of the infection, 0 is the lowest, can only be increased
        self.errors = 0
        self.bad_database = False  # Set to true if the database is not valid
        self.test_run = {}

        self.loaded_test_modules = {}
        self.loaded_test_classes = {}
        self.list_of_tests = []
        self.dict_of_processes = {}  # To get a more granular view of the processes
        self.update_module_list()

        self.base_data = {}
        self.finished_tests = deque()

        self.open_base_data()
        self.exec_all_tests()

    def update_threat(self, threat_level: int):
        """
        Updates the threat level
        :param threat_level: The new threat level
        """
        self.threat_level = max(threat_level, self.threat_level)

    def open_base_data(self) -> dict:
        """
        Opens the base data file
        :return: The base data (a json file)
        """

        default_database = resource_path(self.agnostic_path.default_database)
        if not self.args.database:
            self.args.database = default_database

        if os.path.exists(self.args.database):
            print(colored(f" > Opening specified database {self.args.database}", "green"))  # TODO : Only if verbose
            with open(self.args.database, "r") as f:
                self.base_data = json.load(f)
                self.check_database()
            return self.base_data
        elif os.path.exists(resource_path(default_database)):  # Try opening the default database
            print(colored(
                "\n > The database file specified does not exist, "
                "trying to open the default one for your os...\n", "yellow"
            ))
            with open(resource_path(default_database), "r") as f:
                self.base_data = json.load(f)
                self.check_database()
            return self.base_data

        else:
            print(colored(
                "\n > The database file does not exist, and the default "
                "one for your os does not exist either.\n", "red"
            ))
            self.bad_database = True
            self.base_data = {}
            return self.base_data

    def check_database(self) -> bool:  # TODO: All of this can be refactored with a function
        """
        Check if the database is valid set self.bad_database to True if it is not
        :return: True if the database is valid
        """
        if not self.base_data:
            print(colored(" > The database is empty", "red"))
            self.bad_database = True
            return False

        if "global" not in self.base_data:
            print(colored(" > The database is missing the global section", "red"))
            self.bad_database = True
        else:
            if "discord_version" not in self.base_data["global"]:
                print(colored(" > The database is missing a version field", "red"))
                self.bad_database = True
            else:
                if self.base_data["global"]["discord_version"] != self.version:
                    print(colored(
                        f" > The database is from a different version ({self.base_data['global']['discord_version']}),"
                        f" you are using {self.version}", "red"
                    ))
                    self.bad_database = True
            if "ptb" not in self.base_data["global"]:
                print(colored(" > The database is missing a ptb field", "red"))
                self.bad_database = True
            else:
                if self.base_data["global"]["ptb"] != self.ptb:
                    print(colored(
                        f' > The database is for Discord {self.base_data["global"]["ptb"]} '
                        f'you are using Discord{self.ptb}', "red"
                    ))
                    self.bad_database = True
            if "os" not in self.base_data["global"]:
                print(colored(" > The database is missing an os field", "red"))
                self.bad_database = True
            else:
                if self.base_data["global"]["os"] != self.os_name:
                    print(colored(
                        f" > The database is for {self.base_data['global']['os']}, you are using {self.os_name}", "red"
                    ))
                    self.bad_database = True
        if "tests" not in self.base_data:
            print(colored(" > The database is missing the test results", "red"))
            self.bad_database = True
        else:
            for test_name in self.selected_tests:
                found_one_value = False
                for file_name, test_names in self.base_data["tests"].items():
                    if test_name in test_names:
                        found_one_value = True
                        break  # At least one test is in the database
                if not found_one_value:
                    print(colored(f" > The database is missing the test {test_name}", "red"))
                    self.bad_database = True

    def update_module_list(self) -> List[str]:
        """
        Gets the list of modules to be loaded (in accordance to the config)
        :return: List of modules
        """
        modules = {}
        classes = {}
        module_name = None
        try:
            for module_name, values in _TEST_MODULES.items():
                if self.args.all or self.args.__getattribute__(module_name):
                    modules[values[0]] = importlib.import_module(f"modules.{values[0]}")
                    classes[values[0]] = getattr(modules[values[0]], values[1])
                    self.selected_tests.append(values[1])

        except AttributeError as e:
            print(f"The module {module_name} was not loaded because it was not specified in the config.")
            print(e)

        self.loaded_test_modules.update(modules)
        self.loaded_test_classes.update(classes)

    def exec_all_tests(self) -> None:
        """
        Executes all the tests, get their result as they finishes
        """
        self.list_of_tests = []
        for module_name, test_class in self.loaded_test_classes.items():
            print(colored(f"  > Starting test {module_name}...", "blue"))
            tc = test_class(thread_parameters(
                args=self.args,
                agnpath=self.agnostic_path,
                test_data=self.base_data,
                queue=self.finished_tests,
                queue_lock=queue_lock,
                dict_process=self.dict_of_processes,
                dict_process_lock=processes_lock,
                bad_database=self.bad_database,
            ))
            tc = threading.Thread(target=tc.run, args=())
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

    def controller_test(self) -> None:
        """
        Kills the tests if the user press enter
        """
        print(colored("\n > All test started, press ENTER to abort...\n", "blue"))
        while True:
            # print("Controller still up")
            try:
                if input() == "":
                    global POST_RUN_ALLOWED, RUN_OVER
                    print(colored("\n > Aborting tests...\n", "red"))
                    if not self.is_infected:
                        POST_RUN_ALLOWED = True
                    RUN_OVER = True
                    return
            except KeyboardInterrupt:
                RUN_OVER = True
                return
            except Exception:
                sys.exit()

    def post_test_runner(self) -> None:
        """
        Runs the post test runner if all tests are finished
        """
        global POST_RUN_ALLOWED, RUN_OVER
        if self.args.launch:
            while True:
                if RUN_OVER:
                    if POST_RUN_ALLOWED and self.is_infected == 0:  # Second part is redundant
                        print(colored("\n  > Running post test runner...", "green"))
                        if self.agnostic_path.os == "windows":
                            subprocess.Popen([self.agnostic_path.main_path + f"\\Discord{self.agnostic_path.ptb}.exe"])
                        return 0
                    return 1
                time.sleep(0.1)
        return 0

    def test_waiter(self) -> None:
        """
        Waits for the end of the tests
        """
        for t in self.list_of_tests:  # Can only proceed if all tests are finished
            t.join()
        self.get_status()
        # time.sleep(0.5)
        # When all tests are finished or the user stopped the tests, we can proceed
        if self.is_infected == 0:
            global POST_RUN_ALLOWED
            POST_RUN_ALLOWED = True

    def get_exit_code(self) -> int:  # TODO: Use a NamedTuple
        """
        Gets the exit code of the tests
        :return: The exit code
        """
        status = self.get_status()
        if status.tests_finished == status.tests_total:
            if status.tests_failed != 0:
                exit_code = 1  # There is one failure, so the test failed
            elif status.tests_success == status.tests_total:
                exit_code = 0  # All tests passed
            else:
                # print("Something went wrong, please report this bug.")
                # print(status)
                exit_code = 2  # Something went wrong
        else:
            global RUN_OVER
            if RUN_OVER:
                print(colored("\n  > Tests aborted, please check the logs.", "red"))
                exit_code = 3
            else:
                exit_code = -1  # The tests are not finished
        return exit_code

    def get_status(self) -> internal_io.global_status:
        """
        Gets the status of the tests
        :return: The status
        """
        queue_lock.acquire(timeout=0.5)
        nb_tests = len(self.list_of_tests)
        nb_tests_success = 0
        nb_tests_failure = 0
        nb_tests_skipped = 0
        nb_tests_error = 0
        progress = 0
        for test in self.finished_tests:
            if test.status == "success":
                nb_tests_success += 1
            elif test.status == "failure":
                nb_tests_failure += 1
                self.is_infected += 1
            elif test.status == "skipped":
                nb_tests_skipped += 1
            elif test.status == "problem":
                nb_tests_error += 1
            # progress += test.progress
        queue_lock.release()

        for test_name, test in self.dict_of_processes.items():
            progress += test.progress
        if nb_tests == 0:
            progress = 100
        else:
            progress = int(progress / nb_tests)

        nb_tests_ran = nb_tests_success + nb_tests_failure + nb_tests_skipped + nb_tests_error
        nb_test_running = nb_tests - nb_tests_ran
        return global_status(
            tests_total=nb_tests,
            tests_finished=nb_tests_ran,
            tests_success=nb_tests_success,
            tests_failed=nb_tests_failure,
            tests_running=nb_test_running,
            tests_skipped=nb_tests_skipped,
            tests_error=nb_tests_error,
            progress=progress
        )

    def get_test_data(self) -> dict:
        """
        Gets the test data
        :return: The test data
        """
        data = {}
        queue_lock.acquire()
        for test in self.finished_tests:
            for key, value in test.data.items():
                if key not in data:
                    data[key] = value
                else:
                    data[key].update(value)
        queue_lock.release()
        return data


def export_data(test_runner: TestRunner, data: dict) -> dict:
    """
    Exports the test data and returns it
    :param test_runner: The test runner
    :param data: The test data
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


def print_status(status: internal_io.global_status, timer_start: float) -> None:
    """
    Prints the status
    :param status: The status
    :param timer_start: The start time of the tests
    """
    if status.tests_failed != 0:
        color = "red"
    else:
        color = "green"

    print(colored("\n > Status:", color))
    if status.tests_total == 0:
        print(colored("  > No test found", "red"))
        return

    print(colored(
        f"   > Test finished {status.tests_finished}/{status.tests_total}"
        f": {status.tests_success} success, "
        f"{status.tests_failed} failed, "
        f"{status.tests_error} problem", color
    ))
    if status.tests_running != 0:
        ellapsed_time = time.time() - timer_start
        if status.progress == 0:
            estimated_time = "∞"
        else:
            mon, sec = divmod(ellapsed_time * 100 / status.progress, 60)
            hr, mon = divmod(mon, 60)
            sec = round(sec, 0) + 1
            estimated_time = f"{hr:n}:{mon:02n}:{sec:02.0n}"
        print(colored(
            f"   > Overall progress: {status.progress}%"
            f" in {time.time() - timer_start:.2f} seconds"
            f" estimaded total time ({estimated_time})", color
        ))


def run_check(args: argparse.Namespace, agnpath: agnostic_paths.AgnosticPaths) -> None:
    """
    Runs all operations selected in the config
    :param args: List of arguments
    :param agnpath: Annostic path to the discord folder
    """
    # Initialize the test runner
    print(LOGO)
    start = time.time()
    tr = TestRunner(args, agnpath, start_time=start)  # All operation are executed in parallel and the user can stop them

    # Poll information from the tests
    POLLRATE, PRINT_RATE, COUNTER = args.pollrate, args.printrate, 1
    COUNTER_MAX = int(PRINT_RATE / POLLRATE)

    # Main test polling loop
    while tr.get_exit_code() == -1:
        if (COUNTER % COUNTER_MAX) == 0:
            print_status(tr.get_status(), start)
        time.sleep(POLLRATE)
        COUNTER += 1

    # Print the final status
    global RUN_OVER
    RUN_OVER = True

    # Final status
    print_final_status(tr, start, args)

    # Export the data
    if args.gen_data:
        gen_save_data(args, tr)

    # Sleep for a while to let the user see the final status
    time.sleep(args.timeout)
    sys.exit(tr.get_exit_code())


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # noqa # TODO: Detect if archive, likely with a ugly global check
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def print_final_status(testrunner: TestRunner, start_time: float, args: argparse.Namespace) -> None:
    """
    Prints the final status
    """
    status = testrunner.get_status()
    if status.tests_failed == 0 and status.tests_error == 0 and status.tests_total != 0:
        color = "green"
        print(CLEAR_CODE)
    elif status.tests_failed > 0:
        color = "red"
        print(INFECTED_CODE)
    else:
        color = "yellow"
        print(UNKNOWN_CODE)

    print(colored(
        f"\nThe test sequence is now finished, DiscordHelper ran for "
        f"{round(time.time() - start_time,2)} seconds", color
    ))
    SIZE = args.size
    for test, test_object in testrunner.dict_of_processes.items():
        if test_object.status_code == "success":
            print(colored(f"  > {fill_it(SIZE,test,'SUCCESS')}", "green"))
        elif test_object.status_code == "failure":
            print(colored(f"  > {fill_it(SIZE,test,'FAILURE')}", "red"))
            error_message = "\n".join(at_max_elements(
                fit_it_under(test_object.status, SIZE-3, '    > '), args.max_shown, "     > ... "))
            print(colored(f"{error_message}", "red"))
        elif test_object.status_code == "problem":
            print(colored(f"  > {fill_it(SIZE,test,'PROBLEM')}", "yellow"))
            error_message = "\n".join(at_max_elements(
                fit_it_under(test_object.status, SIZE-3, '    > '), args.max_shown, "     > ... "))
            print(colored(f"{error_message}", "yellow"))
        else:
            print(colored(f"  > {fill_it(SIZE,test,test_object.status_code.upper())}", "yellow"))
    msg_error = "sucessfully" if status.tests_failed == 0 else f"with {status.tests_error} errors"
    print(colored(f"\nThe program executed {msg_error}, exiting in {args.timeout} seconds...", color))


def fill_it(size: int, string1: str, string2: str) -> str:
    """
    Makes a string with the format "string1......string2"
    with as many "." as needed to fill the size
    """
    return string1 + max(size - len(string1)-len(string2), 0) * "." + string2


def at_max_elements(table: list, msize: int, fill: str) -> list:
    """
    Display at maximum msize elements, replace last with fill and return the table
    """
    if msize == -1:
        return table

    # if en(table) > lmsize:
    table = table[:msize] + [
        fill+"..."+str(len(table)-msize)+" more lines" if len(table) > msize else ""]
    return table


def fit_it_under(message: str, size: int, start_line: str = "") -> list:
    """
    Fits a message under a size (split lines into multiple lines if needed) and returns the list of lines
    """
    final_message = []
    for line in message.split('\n'):
        if len(line) > size:
            final_message += [start_line + line[:size]]
            final_message += fit_it_under(line[size:], size, start_line)
        else:
            final_message += [start_line + line]
    return final_message


def gen_save_data(args: argparse.Namespace, test_runner: TestRunner) -> None:
    """
    Generates the save data and writes it to a file
    """
    print(colored("\n  > Generating data...", "blue"))
    data = test_runner.get_test_data()
    file_path = os.path.join(os.path.join("databases", args.gen_data[0]))
    folder = os.path.dirname(file_path)
    if not os.path.exists(folder):
        print(colored("  > Making folder...", "blue"))
        os.makedirs(folder)
    print(colored(f"  > Exporting the test data to {file_path}", "blue"))
    main_data = export_data(test_runner, data)
    # print(main_data)
    with open(file_path, "w") as f:
        json.dump(main_data, f, indent=4)
