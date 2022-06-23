"""
A windows executable for the discordHelper.py script.
"""

import sys

import discordHelper

# All modules must be loaded before the main program is run.
from modules import spidey_test, test_template


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) <= 1:
        argv += "--spidey --launch --test-walk --continue --gen-data new.yaml".split(" ")

    args = discordHelper.argument_parser.parse(argv)
    discordHelper.main(args)
