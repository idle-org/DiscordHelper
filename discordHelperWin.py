"""
A windows executable for the discordHelper.py script.
"""
import os
import sys
import discordHelper
import time

# All modules must be loaded before the main program is run.
from modules import spidey_test, test_template

if __name__ == "__main__":
    try:
        argv = sys.argv[1:]
        if len(argv) == 0:
            user_path = os.path.join(os.path.expanduser("~"), "Documents", "DiscordHelper")
            argv = f"--all --autodetect --launch --continue --timeout 10 --gen-data {user_path}/new_test_data_{int(time.time())}.yaml".split(" ")

        args = discordHelper.argument_parser.parse(argv)

        discordHelper.main(args)
    except Exception as e:
        print(e)
        print("An error occured, please check the console for more information...")
        time.sleep(5)
        sys.exit(1)
