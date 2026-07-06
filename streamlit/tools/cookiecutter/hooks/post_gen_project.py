import os
import shutil

source_dir = os.getcwd()
target_dir = "../projects/"

shutil.move(source_dir, target_dir)
# sym link to common dir
os.symlink("../common/", "common")
os.symlink("../common/debug_page.py", "pages/debug_page.py")
