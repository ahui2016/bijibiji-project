from .bijiscanner import scan_all
from ..bijidb.bijidatabase import BijiDatabase

if __name__ == '__main__':
    from .. import change_cwd
    change_cwd()

    biji_db = BijiDatabase
    biji_db.connect_db()
    scan_all(biji_db)
    biji_db.close_db()
