import asyncio
import os
import time

from modules import test_template


class SizeTest(test_template.TestWalkTemplate):
    def __init__(self, args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock):
        """
        Simple test runner, compare file size to known good values.
        """
        super().__init__(args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock)

    def run_test(self):
        """
        Walk all files and check their size.
        :return: Whether any of the files are larger than the expected size.
        :rtype: bool
        """
        self.set_status("running")
        size = len(self.walk())
        error_msg = ""
        for i, path in enumerate(self.walk()):
            self.progress = int(100*i/size)
            short_path = self.agnostic_path.get_short_path(path)
            if os.path.isfile(path):
                if not self.compare(path, "size", os.path.getsize, (), {}):
                    self.add_failure(path, f"Test {self.name()} failed on {short_path}")
                    error_msg += f"{short_path} is " \
                                 f"({os.path.getsize(path)} b) not ({self.get_expected_result(path, 'size')} b).\n"
                    self.is_infected = True
                    if not self.args.continue_on_error:
                        return self.finish("failure", f"{short_path} is supposed to be {self.get_expected_result(path, 'size')} bytes, but it is {os.path.getsize(path)} bytes.")

        if self.is_infected:
            return self.finish(
                "failure",
                error_msg
            )
        self.progress = 100
        return self.finish("success", "Your discord is not infected.")

