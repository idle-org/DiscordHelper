import os
import re
import sys


class SpideyDetector:
    def __init__(self, args):
        """
        :param ptb: Whether you're using discord Public Test Version
        :type ptb: bool
        """
        if args.ptb:
            self.ptb = "PTB"
        else:
            self.ptb = ""
        self.is_windows = self.check_os()
        self.is_infected = False
        self.paths = self.check_paths(*self.get_path())
        self.spidey_check()

    def check_os(self):  # noqa
        if not sys.platform.startswith('win'):
            raise OSError("This script can only check for Spideys on Windows.")
        return True

    def get_path(self):
        """
        Gets the path of the two folders we need to check
        :return: Two paths.
        :rtype: str
        """
        pre_version_path = os.path.join(os.path.expanduser('~'), "AppData", "Local", f"Discord{self.ptb}")
        version = self.get_version(pre_version_path)
        discord_modules = os.path.join(pre_version_path, version,
                                       "modules", "discord_modules-1", "discord_modules")
        discord_desktop_core = os.path.join(pre_version_path, version,
                                            "modules", "discord_desktop_core-1", "discord_desktop_core")
        return discord_modules, discord_desktop_core

    def get_version(self, pre_version_path):  # noqa I swear this one is not static :(
        """
        Looks for the version file in the discord folder
        :param pre_version_path: the /discord/ path.
        :type pre_version_path: str
        :return: The folder in /discord/ that's only made of ints and dots.
        :rtype: str
        """
        version = None
        for element in os.listdir(pre_version_path):
            if re.match(r"app-[\d\.]+", element):
                version = element
        if not version:
            raise FileNotFoundError("Could not find discord version folder.")
        return version

    def check_paths(self, discord_modules, discord_desktop_core):  # noqa
        if not os.path.isfile(os.path.join(discord_modules, 'index.js')):
            raise FileNotFoundError(f"Could not find index.js in {discord_modules}")
        if not os.path.isfile(os.path.join(discord_desktop_core, 'index.js')):
            raise FileNotFoundError(f"Could not find index.js in {discord_desktop_core}")
        return discord_modules, discord_desktop_core

    def spidey_check(self):
        """
        Counts the number of lines in both index.js files. If it's more than one, it's almost certain your discord
        is corrupted.
        :return: Whether any of the index.js is more than one line
        :rtype: bool
        """
        lines = 0
        with open(os.path.join(self.paths[0], "index.js")) as f:
            for line in f:
                lines = lines + 1
        if lines > 1:
            self.is_infected = True

        lines = 0
        with open(os.path.join(self.paths[1], "index.js")) as f:
            for line in f:
                lines = lines + 1
        if lines > 1:
            self.is_infected = True

        if self.is_infected:
            print("\n!!! WARNING !!!\n"
                  "Unless you've installed a plugin you really trust, chances are your discord install "
                  "is corrupted. We suggest uninstalling discord and deleting all its files before reinstalling.\n"
                  "If you've recently downloaded a .exe directly sent from someone, "
                  "do also consider a clean windows reinstall.")
        return self.is_infected


def run_check(ptb):
    spd = SpideyDetector(ptb)
    if not spd.is_infected:
        return 0
    else:
        return 1


if __name__ == "__main__":
    pass
