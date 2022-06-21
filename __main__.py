#!/usr/bin/python3

""" Main program """

from modules import spidey_detector
import argparse
import sys


def parse(_args):
    parser = argparse.ArgumentParser(
        prog="Spidey Detector",
        description='Checks for corrupt discord install'
    )
    parser.add_argument('ptb', help="Set to True if you're using the PTB")
    return parser.parse_args(_args)


if __name__ == "__main__":
    args = parse(sys.argv)
    try:
        spd = spidey_detector.run_check(args)
    except FileNotFoundError as er:
        print(er)
        sys.exit(1)
    except OSError as er:
        print(er.strerror)
        sys.exit(1)

    if spd == 0:
        print("SpideyDetector could not find anything wrong with your discord install!")
    sys.exit(spd)
