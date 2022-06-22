import argparse


def parse(_args):
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
    parser.add_argument("--force-path", nargs=1, default=None, help="Bypass the automatic path discovery with given path")
    parser.add_argument("--only-known-paths", "--fast", action='store_true', help="Only run the check on the known paths")
    parser.add_argument("--no-eval", action="store_true", help="Check for the eval function wich is a HUGE red flag")
    parser.add_argument("--const-abuse", "--no-const", action="store_true", help="Check for the abuse of the const: keyword, wich is massively used for obfucation")
    parser.add_argument("--gen-data", "--generate-data", "--gen", action="store_true", help="Generate data for the analysis")
    parser.add_argument("--gen-data-path", "--generate-data-path", "--gen-path", nargs=1, default="", help="Path to generate the data in")
    parser.add_argument("--database", "--db", nargs=1, default="", help="Alternative database for the analysis")
    parser.add_argument("--continue", action="store_true", help="Continue the analysis in case of failure")

    return parser.parse_args(_args)