"""
A windows executable for the discordHelper.py script.
"""

import sys

import discordHelper
import time

# All modules must be loaded before the main program is run.
from modules import spidey_test, test_template


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) == 0:
        argv = f"--all --launch --continue --gen-data new{int(time.time())}.yaml".split(" ")
    args = discordHelper.argument_parser.parse(argv)
    discordHelper.main(args)
