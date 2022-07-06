# R: Lists the file tree with the current directory as a root
import os
from pathlib import Path

curr_dir = os.getcwd()

# R: Listing the file tree with the current directory as a root
for name, subdirs, files in os.walk(curr_dir):
    indent = len(Path(name).parts) - len(Path(curr_dir).parts)
    print("    " * indent + Path(name).parts[-1] + os.sep)
    for index, filename in enumerate(sorted(files)):
        if index == 3:
            print("    " * (indent + 1) + "...")
            break
        print("    " * (indent + 1) + filename)
