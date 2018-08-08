from .bijiscanner import delete_biji_json_not_exists
from ..bijidb.bijidatabase import BijiDatabase

if __name__ == '__main__':
    from .. import change_cwd
    change_cwd()

    biji_db = BijiDatabase
    biji_db.connect_db()
    delete_biji_json_not_exists(biji_db)
    biji_db.close_db()
