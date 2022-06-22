import os
import re
import sys
import importlib

"""
All modules that can be tested
Associate the arguments passed to the command line with the modules to be loaded
argparse argument : [module_name, class_name]
"""
_TEST_MODULES = {
    "spidey": ["spidey_test", "SpideyTest"],
}


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
        self.update_module_list()
        self.exec_all_tests()

    def update_module_list(self):
        """
        Gets the list of modules to be loaded (in accordance to the config)
        :return: List of modules
        :rtype: list
        """
        modules = {}
        classes = {}
        try:
            for module_name, values in _TEST_MODULES.items():
                print(values[0])
                if self.args.__getattribute__(module_name):
                    modules[values[0]] = importlib.import_module(f"modules.{values[0]}")
                    classes[values[0]] = getattr(modules[values[0]], values[1])

        except AttributeError:
            print(f"The module {module_name} was not loaded because it was not specified in the config.")

        self.loaded_test_modules.update(modules)
        self.loaded_test_classes.update(classes)

    def exec_all_tests(self):
        """
        Executes all the tests (later in parallel), get their result as they finishes
        :return: The number of test ran, success, failures, skipped (with ran = success+failures+skip)
        :rtype: (int,int,int,int) # TODO: Change this to a nametuple
        """
        for module_name, test_class in self.loaded_test_classes.items():
            tc = test_class(self.args, self.agnostic_path, None)
            tc.run_test()
            print(tc)


def run_check(args, agnpath):  # Todo, skip the is_infected check and defer everything to the exec_all_tests
    spd = TestRunner(args, agnpath)
    if not spd.is_infected:
        return 0
    else:
        return 1


if __name__ == "__main__":
    pass
