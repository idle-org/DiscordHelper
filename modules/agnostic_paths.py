"""
The agnostic path handler, gives all methods to access all paths of the discord client, regardless of the os.
"""
import os
import re
import sys


class AgnosticPaths:
    def __init__(self, ptb):
        self.ptb = ptb
        self.os = self.get_os()
        self.main_path = self.get_path()
        self.versions = self.get_version()

    def get_os(self):
        platform = sys.platform
        if platform.startswith('win'):
            self.os = 'windows'
        elif platform.startswith('linux'):
            self.os = 'linux'
        elif platform.startswith('darwin'):
            self.os = 'mac'
        else:
            raise OSError("This script can only check for Spideys on Windows, Linux and Mac.")
        return self.os

    def get_path(self):
        if self.os == 'windows':
            return os.path.join(os.path.expanduser('~'), "AppData", "Local", f"Discord{self.ptb}")
        elif self.os == 'linux':
            return os.path.join("/","opt","discord")
            #return os.path.join("usr","share","discord")
        elif self.os == 'mac':
            return ""
        raise OSError("Cannot detect discord PATH")

    def get_version(self):
        """
        Looks for the version file in the discord folder
        """
        versions = []
        if self.os == 'windows':
            for element in os.listdir(self.main_path):
                if re.match(r"app-[\d\.]+", element):
                    versions.append(element)
            if not versions:
                raise FileNotFoundError("Could not find discord version folder.")
            versions.sort()
            return versions[-1]
        if self.os == 'linux':
            from json import load
            with open(os.path.join(self.main_path,'resources','build_info.json')) as versionFile:
                versions = load(versionFile)
            return versions['version']




    def list(self, *args):
        """
        Lists all files in the given path.
        :param args: The path
        """
        return os.listdir(self(*args))

    def list_dir_files(self, *args):
        """
        Lists all files and directories in the given path.
        :param args: The path
        """
        all_files = self.list(*args)
        _path = self(*args)
        files = []
        dirs = []
        for element in all_files:
            if os.path.isdir(os.path.join(_path, element)):
                dirs.append(element)
            else:
                files.append(element)
        return dirs, files

    def __call__(self, *args, version=None):
        if version is None:
            _path = os.path.join(self.main_path, *args)
        elif version == "LATEST":
            _path = os.path.join(self.main_path, self.latest_version, *args)
        else:
            _path = os.path.join(self.main_path, version, *args)
        if not os.path.exists(_path):
            raise FileNotFoundError(f"Could not find {_path}")
        return _path

    def __repr__(self):
        return f"AgnosticPaths(ptb={self.ptb}, os={self.os}, main_path={self.main_path}, version={self.latest_version})"

    def __str__(self):
        return self.main_path


if __name__ == '__main__':
    path = AgnosticPaths("")
    print(path)
    print(path.versions)
    print(path.list_dir_files())
    print(path.list())
