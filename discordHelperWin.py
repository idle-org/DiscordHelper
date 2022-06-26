"""
A windows executable for the discordHelper.py script.
"""
import os
import sys
import discordHelper
import time

# All modules must be loaded before the main program is run.
from modules import spidey_test, test_template  # noqa # Set for pyinstaller

if __name__ == "__main__":
    try:
        argv = sys.argv[1:]
        if len(argv) == 0:
            directory_path = os.path.join(os.getcwd(), "discordHelper")
            db_path = os.path.join(directory_path, "windows_base.json")
            argv = ["-p", db_path]
            if os.path.exists(db_path):
                # print("  > A user database was found it will be used instead of the bundled one.")
                # print("  > If you want to use the bundled database, delete the file: " + db_path)
                db_path = "--database " + db_path + " "
            else:
                db_path = ""
                # print("  > No user database was found, the bundled one will be used.")

            # Will always try to load discordHelper/discordHelper.json # TODO : Document this feature.
            run_db = os.path.join(directory_path, "test_results_found.json")
            argv = rf"--all --autodetect --launch --continue --timeout 10 {db_path}--gen-data {run_db} --db discordHelper/test_results.json".split(" ")
        # print("  > Starting the discordHelper with the following arguments:")
        # print("    > " + " ".join(argv))

        args = discordHelper.argument_parser.parse(argv)

        discordHelper.main(args)
    except Exception as e:
        print(e)
        print("  > An error occured, please check the console for more information...")
        time.sleep(5)
        raise SystemExit
