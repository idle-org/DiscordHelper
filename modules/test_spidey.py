import os

from modules import test_template, internal_io


class SpideyTest(test_template.TestTemplate):
    def __init__(self, thread_parameters: internal_io.thread_parameters):
        """
        Simple test runner, for testing the detection of Spidey viruses.
        """
        super().__init__(thread_parameters)

    def run_test(self) -> str:
        """
        Counts the number of lines in both index.js files. If it's more than one, it's almost certain your discord
        is corrupted.
        :return: The status of the test as a string.
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

        if self.is_infected:
            return self.finish(
                "failure",
                "Unless you've installed a plugin you really trust, chances are your discord install "
                "is corrupted. We suggest uninstalling discord and deleting all its files before reinstalling.\n"
                "If you've recently downloaded a .exe directly sent from someone, "
                "do also consider a clean windows reinstall."
            )
        self.add_to_new_data("global_tests", self.name(), "passed")
        self.progress = 100
        return self.finish("success", "Your discord is not infected.")

    def get_path(self) -> str:
        """
        Gets the path of the two folders we need to check
        :return: Two paths.
        """
        discord_modules = self.agnostic_path("modules", "discord_modules-1", "discord_modules")
        discord_desktop_core = self.agnostic_path("modules", "discord_desktop_core-1", "discord_desktop_core")
        return discord_modules, discord_desktop_core
