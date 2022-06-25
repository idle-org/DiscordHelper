import asyncio
import os
import time

from modules import test_template


class SpideyTest(test_template.TestTemplate):
    def __init__(self, args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock):
        """
        Simple test runner, for testing the detection of Spidey viruses.
        """
        super().__init__(args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock)

    def run_test(self):
        """
        Counts the number of lines in both index.js files. If it's more than one, it's almost certain your discord
        is corrupted.
        :return: Whether any of the index.js is more than one line
        :rtype: bool
        """
        self.set_status("running")

        paths = self.get_path()
        self.is_infected = False
        lines = 0
        with open(os.path.join(paths[0], "index.js")) as f:
            for _ in f:
                lines += 1
                if lines > 1:
                    self.is_infected = True
                    break

        self.progress = 50
        # time.sleep(5)
        lines = 0

        with open(os.path.join(paths[1], "index.js")) as f:
            for _ in f:
                lines += 1
                if lines > 1:
                    self.is_infected = True
                    break

        # self.is_infected = True
        if self.is_infected:  # TODO: set a status here, explaining and why the test failed, the scary part will be handled by the main program
            return self.finish("failure", "\n!!! WARNING !!!\n"
                  "Unless you've installed a plugin you really trust, chances are your discord install "
                  "is corrupted. We suggest uninstalling discord and deleting all its files before reinstalling.\n"
                  "If you've recently downloaded a .exe directly sent from someone, "
                  "do also consider a clean windows reinstall.")

        self.progress = 100
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
