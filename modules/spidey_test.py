import asyncio
import os


class SpideyTest:
    def __init__(self, args, agnpath, test_data):
        """
        Simple test runner, for testing the detection of Spidey viruses.
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
        self.alive = True

    def run_test(self):
        """
        Counts the number of lines in both index.js files. If it's more than one, it's almost certain your discord
        is corrupted.
        :return: Whether any of the index.js is more than one line
        :rtype: bool
        """
        import random, time
        # Wait a random amount of time to make sure the files are loaded
        time.sleep(random.randint(1, 5))
        paths = self.get_path()
        self.is_infected = False
        lines = 0
        with open(os.path.join(paths[0], "index.js")) as f:
            for line in f:
                lines += 1
        if lines > 1:
            self.is_infected = True

        lines = 0
        with open(os.path.join(paths[1], "index.js")) as f:
            for line in f:
                lines += 1
        if lines > 1:
            self.is_infected = True

        if self.is_infected:
            print("\n!!! WARNING !!!\n"
                  "Unless you've installed a plugin you really trust, chances are your discord install "
                  "is corrupted. We suggest uninstalling discord and deleting all its files before reinstalling.\n"
                  "If you've recently downloaded a .exe directly sent from someone, "
                  "do also consider a clean windows reinstall.")
        return self.is_infected

    def get_path(self):
        """
        Gets the path of the two folders we need to check
        :return: Two paths.
        :rtype: str
        """
        discord_modules = self.agnostic_path("modules", "discord_modules-1", "discord_modules")
        discord_desktop_core = self.agnostic_path("modules", "discord_desktop_core-1", "discord_desktop_core")
        return discord_modules, discord_desktop_core

    def get_status_code(self):
        """
        The status code of the test
        :return: 0: The test was not run, 1: The test is running, 2: The test is a success, 3: Test has failed, 4: Test found problems
        :rtype: int
        """
        # TODO: Add this to a global_dict
        return 0

    def get_status(self):
        """
        Return the status of the test, as a string, as the test is ran
        :return: "Test is running", "Test was not run", "Test was run and nothing was detected", "Test was run and some problems were detected (list of problems)"
        :rtype: (int, str)
        """
        # TODO: Make use of a global_dict
        return self.get_status_code(), ""


async def main(args, agnpath, test_data):
    """
    The main function of the test.
    :return: The status of the test
    :rtype: (int, str)
    """
    spidey_test = SpideyTest(args, agnpath, test_data)
    await asyncio.sleep(5)
    spidey_test.run_test()
    return spidey_test.get_status()
