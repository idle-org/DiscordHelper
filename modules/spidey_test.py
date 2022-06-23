import asyncio
import os
from modules import test_template


class SpideyTest(test_template.TestTemplate):
    def __init__(self, args, agnpath, test_data, queue, queue_lock):
        """
        Simple test runner, for testing the detection of Spidey viruses.
        """
        super().__init__(args, agnpath, test_data, queue, queue_lock)

    def slowdown(self):
        """
        This function is only used for testing.
        :return:
        """
        print("Spidey test is running slowly...")
        import random, time
        time.sleep(random.randint(1, 5))

    def run_test(self):
        """
        Counts the number of lines in both index.js files. If it's more than one, it's almost certain your discord
        is corrupted.
        :return: Whether any of the index.js is more than one line
        :rtype: bool
        """
        self.set_status("running")
        self.slowdown()  # This function is only used for testing
        paths = self.get_path()
        self.is_infected = False
        lines = 0
        with open(os.path.join(paths[0], "index.js")) as f:
            for line in f:
                lines += 1  # TODO: you don't actually need to count the lines, you can just check if it's more than 1
        if lines > 1:
            self.is_infected = True

        lines = 0
        with open(os.path.join(paths[1], "index.js")) as f:
            for line in f:
                lines += 1  # TODO: you don't actually need to count the lines, you can just check if it's more than 1
        if lines > 1:
            self.is_infected = True

        if self.is_infected:  # TODO: set a status here, explaining and why the test failed, the scary part will be handled by the main program
            print("\n!!! WARNING !!!\n"
                  "Unless you've installed a plugin you really trust, chances are your discord install "
                  "is corrupted. We suggest uninstalling discord and deleting all its files before reinstalling.\n"
                  "If you've recently downloaded a .exe directly sent from someone, "
                  "do also consider a clean windows reinstall.")
        print("Spidey test finished") # TODO : set a status here, explaining and why the test finished

        return self.finish("success")

    def get_path(self):
        """
        Gets the path of the two folders we need to check
        :return: Two paths.
        :rtype: str
        """
        discord_modules = self.agnostic_path("modules", "discord_modules-1", "discord_modules")
        discord_desktop_core = self.agnostic_path("modules", "discord_desktop_core-1", "discord_desktop_core")
        return discord_modules, discord_desktop_core
