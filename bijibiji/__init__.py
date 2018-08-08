import os
from pathlib import Path

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
BASE_FOLDER = 'HOME'
TESTING_BASE_FOLDER = 'unittesting_mock'
FILES_FOLDER = BASE_PATH.joinpath(BASE_FOLDER)
TESTING_FILES_FOLDER = BASE_PATH.joinpath(TESTING_BASE_FOLDER)

DB_NAME = 'biji_database.db'

def change_cwd(testing=False):
    if testing:
        os.chdir(str(TESTING_FILES_FOLDER))
    else:
        os.chdir(str(FILES_FOLDER))
