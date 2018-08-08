from .bijiscanner import print_all_biji_in_db
from ..bijidb.bijidatabase import BijiDatabase

if __name__ == '__main__':
    from .. import change_cwd
    change_cwd()

    biji_db = BijiDatabase
    biji_db.connect_db()
    print_all_biji_in_db(biji_db)
    biji_db.close_db()
