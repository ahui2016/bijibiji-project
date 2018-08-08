from .bijiscanner import scan_all_and_update_db
from ..bijidb.bijidatabase import BijiDatabase

if __name__ == '__main__':
    from .. import change_cwd
    change_cwd()

    biji_db = BijiDatabase

    try:
        biji_db.connect_db()
    except FileNotFoundError:
        biji_db.create_db()
        biji_db.connect_db()

    scan_all_and_update_db(biji_db)
    biji_db.close_db()
