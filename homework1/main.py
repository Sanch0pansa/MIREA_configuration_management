from Emulator import Emulator
import sys
import os

if len(sys.argv) < 4:
    print("Incorrect arguments number")
else:
    username = sys.argv[1]
    path_to_archive = sys.argv[2]

    if not os.path.exists(path_to_archive):
        print("Incorrect path to archive")

    path_to_log = sys.argv[3]

    emulator = Emulator(username, path_to_archive, path_to_log)
    emulator.run_emulator()