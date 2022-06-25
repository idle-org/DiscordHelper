"""
Fast adler32 checksum implementation.
"""
import os

from modules import test_template
from zlib import adler32


def apply_adler(path):
    """
    Apply the adler32 checksum to a file.
    :param path: The path to the file.
    :type path: str
    :return: The adler32 checksum.
    :rtype: int
    """
    with open(path, "rb") as f:
        return hex(adler32(f.read()))


class AdlerTest(test_template.TestWalkTemplateNoLogs):
    def __init__(self, args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock):
        """
        Simple test runner, compare adler32 to known good values.
        """
        super().__init__(args, agnpath, test_data, queue, queue_lock, dict_process, dict_process_lock)

    def run_test(self):
        self.set_status("running")
        size = len(self.walk())
        error_msg = ""
        for i, path in enumerate(self.walk()):
            self.progress = int(100*i/size)
            short_path = self.agnostic_path.get_short_path(path)
            if os.path.isfile(path):
                if not self.compare(path, "adler32", apply_adler, (), {}):
                    res = self.get_test_data(path, "adler32")
                    self.add_failure(path, f"Test {self.name()} failed on {short_path}")
                    error_msg += f"{short_path} is " \
                                 f"({res}) not ({self.get_expected_result(path, 'adler32')} b).\n"
                    self.is_infected = True
                    if not self.args.continue_on_error:
                        return self.finish("failure", f"{short_path} is supposed to be {self.get_expected_result(path, 'adler32')} bytes, but it is {adler32(open(path, 'rb').read())} bytes.")

        self.progress = 100
        if self.is_infected:
            return self.finish(
                "failure",
                error_msg
            )
        return self.finish("success", "Your discord is not infected.")