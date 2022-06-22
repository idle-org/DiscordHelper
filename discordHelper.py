#!/usr/bin/python3

""" Main program """

from modules import test_interface, agnostic_paths, argument_parser
import sys


if __name__ == "__main__":
    args = argument_parser.parse(sys.argv[1:])
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
        print("Discord Helper could not find anything wrong with your discord install!")  # TODO: Everything should be in the run_all_tests()
    sys.exit(spd)
