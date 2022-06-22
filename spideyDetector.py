#!/usr/bin/python3

""" Main program """

from modules import test_interface, agnostic_paths
import argparse
import sys


def parse(_args): # TODO: Move this to a arg_parsing module
    parser = argparse.ArgumentParser(
        prog="Spidey Detector",
        description='Checks for corrupt discord install'
    )
    parser.add_argument('--ptb', action='store_const', const="PTB", default="", help='Use Public Test Version')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode')
    parser.add_argument('--spidey', action='store_true', help='Runs the spidey test')
    parser.add_argument('--line-count', action='store_true', help='Test all known files for line count')
    parser.add_argument('--file-count', action='store_true', help="Test the number of files in the discord folder")
    parser.add_argument('--file-size', action='store_true', help="Test the size of the files in the discord folder")
    parser.add_argument('--file-hash', action='store_true', help="Test the hash of the files in the discord folder")
    parser.add_argument('--file-path', action='store_true', help="Test the path of the files in the discord folder")
    parser.add_argument('--file-name', action='store_true', help="Test the name of the files in the discord folder")
    parser.add_argument('--file-extension', action='store_true', help="Test the extension of the files in the discord folder")
    parser.add_argument('--file-date', action='store_true', help="Test the date of the files in the discord folder")
    parser.add_argument('--analyze', action='store_true', help="Analyze the files in the discord folder for known js obfuscators")
    parser.add_argument('--all', action='store_true', help="Run all tests in parallel, and wait for a potential interupt")
    parser.add_argument('--launch', action='store_true', help="Launch the discord client after the tests are done")
    parser.add_argument("--force-path", nargs=1, default="", help="Bypass the automatic path discovery with given path")
    return parser.parse_args(_args)


if __name__ == "__main__":
    args = parse(sys.argv[1:])
    agnostic_path = agnostic_paths.AgnosticPaths(ptb=args.ptb, force_path=args.force_path)
    try:
        spd = test_interface.run_check(args, agnostic_path)

    except FileNotFoundError as er:
        print(er)
        sys.exit(1)
    except OSError as er:
        print(er.strerror)
        sys.exit(1)

    if spd == 0:
        print("TestRunner could not find anything wrong with your discord install!") # TODO: Everything should be in the run_all_tests()
    sys.exit(spd)
