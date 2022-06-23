#!/usr/bin/python3

""" Main program """

from modules import test_interface, agnostic_paths, argument_parser
import sys


if __name__ == "__main__":
    args = argument_parser.parse(sys.argv[1:])
    agnostic_path = agnostic_paths.AgnosticPaths(ptb=args.ptb, force_path=args.force_path)

    test_interface.run_check(args, agnostic_path)