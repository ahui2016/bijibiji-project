from pathlib import Path
from typing import List, Set

from ..bijitags.biji import Biji
from ..bijidb.bijidatabase import BijiDatabase


def scan_all(db: type(BijiDatabase)) -> List[str]:
    """ Return files that both the file itself and the .biji.json exist. """
    files = []
    end = -len('.biji.json')

    biji_paths = Path('.').glob('**/*.biji.json')
    for biji_path in biji_paths:
        file = str(biji_path)[:end]
        if Path(file).exists():
            biji = Biji.from_file(file)
            files.append(file)
        else:
            print(file, '... Not Exists')
            continue

        mtime = db.get_mtime(file)
        if not mtime:
            print(file, '... Not in Database')
            continue

        if biji.bijiMTime > mtime:
            print(file, f'Need to be updated: {mtime} -> {biji.bijiMTime}')

    print(f'There will be {len(files)} items in the database.')
    return files


def scan_all_and_update_db(db: type(BijiDatabase)) -> None:
    end = -len('.biji.json')

    biji_paths = Path('.').glob('**/*.biji.json')
    for biji_path in biji_paths:
        file = str(biji_path)[:end]
        if Path(file).exists():
            biji = Biji.from_file(file)
        else:
            print(file, '... Not Exists')
            continue

        mtime = db.get_mtime(file)
        if not mtime:
            biji.insert_biji_and_tags_to_db()
            print(file, '... added')
            continue

        if biji.bijiMTime > mtime:
            biji.update_biji_and_tags_to_db()
            print(file, '... updated')


def biji_json_not_exists(db: type(BijiDatabase)) -> List[str]:
    """
    Return records that the corresponding .biji.json file does not exist.
    """
    result = []
    for row in db.get_all_filepaths():
        filepath = row['filepath']
        if not Biji.get_biji_json_path(filepath).exists():
            result.append(filepath)
    return result


def delete_biji_json_not_exists(db: type(BijiDatabase)) -> None:
    for row in db.get_all_filepaths():
        filepath = row['filepath']
        if not Biji.get_biji_json_path(filepath).exists():
            db.delete_biji(filepath)
            print(filepath, '... deleted')


def all_biji_in_db(db: type(BijiDatabase)) -> Set[str]:
    result = set()
    for row in db.get_all_filepaths():
        result.add(row['filepath'])
    return result


def print_all_biji_in_db(db: type(BijiDatabase)) -> None:
    for row in db.get_all_filepaths():
        print(row['filepath'])
