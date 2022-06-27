#!/usr/bin/python3

""" Main program """
import argparse

from modules import main_runner, agnostic_paths, argument_parser
import sys


def main(argm: argparse.Namespace):
    """
    Main program
    :param argm: List of arguments
    """
    agnostic_path = agnostic_paths.AgnosticPaths(argm)
    main_runner.run_check(argm, agnostic_path)


if __name__ == "__main__":
    args = argument_parser.parse(sys.argv[1:])
    main(args)
