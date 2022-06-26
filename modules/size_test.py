import os

from modules import test_template


class SizeTest(test_template.TestWalkTemplateNoLogs):
    def __init__(self, thread_parameters):
        """
        Simple test runner, compare file size to known good values.
        """
        super().__init__(thread_parameters)
        self.is_unknown = False

    def run_test(self):
        """
        Walk all files and check their size.
        :return: Whether any of the files are larger than the expected size.
        :rtype: bool
        """
        self.set_status("running")
        size = self.agnostic_path.size

        error_msg = ""
        for i, path in enumerate(self.walk()):
            self.progress = int(100*i/size)
            short_path = self.agnostic_path.get_short_path(path)
            if os.path.isfile(path):
                if not self.compare(path, "size", os.path.getsize, (), {}):
                    res = self.get_test_data(path, "adler32")
                    self.add_failure(path, f"Test {self.name()} failed on {short_path}")
                    error_msg += f"{short_path} is " \
                                 f"({res} b) not ({self.get_expected_result(path, 'size')} b).\n"
                    # print(self.bad_database)
                    if not self.bad_database:
                        self.is_infected = True
                        if not self.args.continue_on_error:
                            return self.finish(
                                "failure",
                                f"{short_path} is supposed to be {self.get_expected_result(path, 'size')}"
                                f" bytes, but it is {os.path.getsize(path)} bytes.")
                    else:
                        self.is_unknown = True
                        if not self.args.continue_on_error:
                            return self.finish(
                                "problem",
                                f"{short_path} is supposed to be {self.get_expected_result(path, 'size')}"
                                f" bytes, but it is {os.path.getsize(path)} bytes.")

        self.progress = 100
        if self.is_infected:
            return self.finish(
                "failure",
                error_msg
            )
        elif self.is_unknown:
            return self.finish(
                "problem",
                error_msg
            )
        return self.finish("success", "Your discord is not infected.")
