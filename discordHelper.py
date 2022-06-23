#!/usr/bin/python3

""" Main program """

from modules import test_interface, agnostic_paths, argument_parser
import sys


def main(argm):
    """
    Main program
    :param argm: List of arguments
    :type argm: argparse.Namespace
    """
    agnostic_path = agnostic_paths.AgnosticPaths(argm.ptb, argm.force_path)
    test_runner = test_interface.run_check(argm, agnostic_path)


if __name__ == "__main__":
    args = argument_parser.parse(sys.argv[1:])
    main(args)
