"""
The agnostic path handler, gives all methods to access all paths of the discord client, regardless of the os.
"""
import os
import re
import sys


class AgnosticPaths:
    """
    An agnostic path object, containing all methods to access the files and folders in a standard discord install
    """
    
    def __init__(self, args):
        """
        :param args: The arguments passed to the script
        :type args: argparse.Namespace
        """
        self.args = args
        self.ptb = args.ptb
        self.os = self.get_os()
        self.default_database = ""
        if args.force_path is not None:
            self.force_path = args.force_path[0]
        else:
            self.force_path = None
        self.main_path = self._get_path()
        self.version = self.get_version()
        self._update_path()

    def get_os(self):
        """
        Get the os string in a short, spydey-detector way.
        For now only windows and linux are supported, note that due to the nature of linux builds, strings will likely become
        linux-arch-deb, linux-arch-snap etc...
        :return: ("windows", "linux", "mac")
        :rtype: str
        """
        
        platform = sys.platform
        if platform.startswith('win'):
            self.os = 'windows'
            self.default_database = 'databases/windows_base.json'
        elif platform.startswith('linux'):
            self.os = 'linux'
            self.default_database = 'databases/linux_base.json'
        elif platform.startswith('darwin'):
            self.os = 'mac'
            self.default_database = 'databases/mac_base.json'
        else:
            raise OSError("This script can only check for Spideys on Windows, Linux and Mac.")
        return self.os

    def _get_path(self):
        """
        Return the base path of the install, note that the self.main_path is not returned,
        and this method is meant to be used at init only
        :return: Base path of the install (minus the version on Windows)
        :rtype: str
        """
        if self.force_path is not None:
            return self.force_path
        if self.os == 'windows':
            base_path = os.path.join(os.path.expanduser('~'), "AppData", "Local", f"Discord")
            ptb_path = base_path+"PTB"
            if self.args.autodetect:
                if os.path.exists(ptb_path):
                    self.ptb = "PTB"
                    self.args.ptb = "PTB"
                    self.default_database = "databases/windows_ptb.json"
                    return ptb_path
                else:
                    self.default_database = "databases/windows_base.json"
                    return base_path
            if self.ptb == 'PTB':
                self.default_database = "databases/windows_bas.jsone"
                return base_path+"PTB"
            else:
                self.default_database = "databases/windows_ptb.json"
                return base_path  # Try to find the default version
        elif self.os == 'linux':
            return os.path.join("/", "opt", "discord")
            # return os.path.join("usr","share","discord")
        elif self.os == 'mac':
            return ""
        raise OSError("Cannot detect discord PATH")

    def get_version(self):
        """
        Looks for the version file in the discord folder 
        and return the latest version of the discord build
        :return: The version build
        :rtype: str
        """
        versions = []
        if self.os == 'windows':
            for element in os.listdir(self._get_path()):
                if re.match(r"app-[\d.]+", element):
                    versions.append(element)
            if not versions:
                raise FileNotFoundError("Could not find discord version folder.")
            versions.sort()
            return versions[-1]
        elif self.os == 'linux':
            from json import load
            with open(self('resources', 'build_info.json'), "r") as versionFile:
                versions = load(versionFile)
            return versions['version']
        else:
            raise OSError("Can't find for version on your OS.")

    def _update_path(self):
        """
        Update the main path with the version, if needed (windows & mac only)
        """
        if self.os == 'windows':
            self.main_path = os.path.join(self.main_path, self.version)

    def list(self, *args):
        """
        Lists all files in the path /discord_path/args[0]/args[1].../args[n]
        :param args: The path as a list of parameters list("folder1", "folder2", ..., "foldern")
        :type args: str
        :return: The list of all files and folders in the given path 
        :rtype: list[str]
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

    def __call__(self, *args):
        """
        Tries to open the path /discord_path/args[0]/args[1].../args[n]
        :param args: The path of the file or directory as a list of parameters __call__("folder1", "folder2", ..., "foldern")
        :type args: str
        :return: The path is it exists
        :rtype: str
        :raises: FileNotFoundError if the path doesn't exists
        """
        _path = os.path.join(self.main_path, *args)
        if not os.path.exists(_path):
            raise FileNotFoundError(f"Could not find {_path}")
        return _path
    
    def get_path(self):
        """
        The main path of the discord install
        :return: self.main_path
        :rtype: str
        """
        return self.main_path

    def walk_all_files(self, *args):
        """
        Walks all files in the given path
        :param args: The path
        :return: A list of all files in the given path
        :rtype: list[str]
        """
        return [os.path.join(dirpath, filename)
                for dirpath, dirnames, filenames in os.walk(self(*args))
                for filename in filenames]

    def get_short_path(self, path):
        """
        Get the short path of the given path
        :param path: The path
        :return: The short path
        :rtype: str
        """
        return os.path.relpath(path, self.main_path)

    def __repr__(self):
        """
        :return: A representation of the AgnosticPath
        :rtype: str
        """
        return f"AgnosticPaths(ptb={self.ptb}, os={self.os}, main_path={self.main_path}, version={self.version})"

    def __str__(self):
        """
        :return: The main path of the discord install
        :rtype: str
        """
        return self.main_path
