import asyncio
import os
from modules import test_template


class SpideyTest(test_template.TestTemplate):
    def __init__(self, args, agnpath, test_data, queue):
        """
        Simple test runner, for testing the detection of Spidey viruses.
        :param args: List of arguments
        :type args: argparse.Namespace
        :param agnpath: The path to the discord folder
        :type agnpath: agnostic_path.AgnosticPath
        :param test_data: The data to be tested
        :type test_data: str
        :param queue: The queue to put the status in
        :type queue: queue.Queue
        """
        super().__init__(args, agnpath, test_data, queue)

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
        print("Spidey test finished")

        self.set_status(0)
        status = self.get_status()
        self.queue.append(status)
        return self.get_status_code()

    def get_path(self):
        """
        Gets the path of the two folders we need to check
        :return: Two paths.
        :rtype: str
        """
        discord_modules = self.agnostic_path("modules", "discord_modules-1", "discord_modules")
        discord_desktop_core = self.agnostic_path("modules", "discord_desktop_core-1", "discord_desktop_core")
        return discord_modules, discord_desktop_core
