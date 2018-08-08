import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Set, List, Tuple

from .. import DB_NAME

CREATE_TABLES = """
    CREATE TABLE bijis (
        filepath    text        PRIMARY KEY COLLATE NOCASE,
        filename    text        NOT NULL,
        suffix      text        NOT NULL,
        mimetype    text,
        filesize    integer     NOT NULL,
        updatedAt   text        NOT NULL,
        backupAt    text        NOT NULL,
        bijiCTime   text        NOT NULL,
        bijiMTime   text        NOT NULL check(bijiMTime <> '')
    );

    CREATE INDEX bijis_filename_idx ON bijis(filename);
    CREATE INDEX bijis_updatedAt_idx ON bijis(updatedAt);
    CREATE INDEX bijis_backupAt_idx ON bijis(backupAt);
    CREATE INDEX bijis_bijiCTime_idx ON bijis(bijiCTime);
    CREATE INDEX bijis_bijiMTime_idx ON bijis(bijiMTime);

    CREATE TABLE tags (
        tag         text        PRIMARY KEY,
        usedAt      text        NOT NULL check(usedAt <> '')
    );

    CREATE INDEX tags_usedAt ON tags(usedat);

    CREATE TABLE tag_biji (
        tag         text        REFERENCES tags(tag)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE,
        filepath    text        REFERENCES bijis(filepath)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE
    );
    """

INSERT_INTO_BIJIS = """
    INSERT INTO bijis (
        filepath,
        filename,
        suffix,
        mimetype,
        filesize,
        updatedAt,
        backupAt,
        bijiCTime,
        bijiMTime
    ) VALUES (
        :filepath,
        :filename,
        :suffix,
        :mimetype,
        :filesize,
        :updatedAt,
        :backupAt,
        :bijiCTime,
        :bijiMTime
    )
    """

INSERT_INTO_TAGS = """
    INSERT INTO tags (tag, usedAt) VALUES (:tag, :usedAt)
    """

INSERT_INTO_TAG_BIJI = """
    INSERT INTO tag_biji (tag, filepath) VALUES (:tag, :filepath)
    """

UPDATE_BIJI = """
    UPDATE bijis SET
        filename = :filename,
        suffix = :suffix,
        mimetype = :mimetype,
        updatedAt = :updatedAt,
        backupAt = :backupAt,
        bijiCTime = :bijiCTime,
        bijiMTime = :bijiMTime
    WHERE filepath = :filepath
    """

DELETE_TAG = """
    DELETE FROM tags WHERE tag = :tag
    """

UNLINK_TAG = """
    DELETE FROM tag_biji WHERE tag = :tag and filepath = :filepath
    """

UPDATE_TAG = """
    UPDATE tags SET tag = :new WHERE tag = :old
    """

UPDATE_TAG_TIME = """
    UPDATE tags SET usedAt = :usedAt WHERE tag = :tag
    """

UPDATE_BIJI_MTIME = """
    UPDATE bijis SET bijiMTime = :bijiMTime WHERE filepath = :filepath
    """

GET_TAGS = """
    SELECT tag FROM tag_biji WHERE filepath = :filepath
    """

GET_BIJIS = """
    SELECT filepath FROM tag_biji WHERE tag = :tag
    """

GET_TAGS_ORDER_BY_COUNT = """
    SELECT tag, COUNT(*) AS count FROM tag_biji GROUP BY tag ORDER BY count
    """

GET_TAGS_ORDER_BY_TAG = """
    SELECT tag FROM tags ORDER BY tag
    """

GET_TAGS_ORDER_BY_TIME = """
    SELECT tag FROM tags ORDER BY usedAt DESC
    """

# GET_TAGS_ORDER_BY_TIME = """
#     SELECT tag_biji.tag, COUNT(*) AS count FROM tag_biji
#     INNER JOIN tags ON tag_biji.tag = tags.tag
#     GROUP BY tag_biji.tag ORDER BY usedAt DESC
#     """

GET_TAGS_NOT_USED = tags_by_count = """
    SELECT tags.tag AS tag FROM tags LEFT OUTER JOIN tag_biji 
    ON tags.tag = tag_biji.tag WHERE tag_biji.tag is NULL
    """

GET_ALL_TAGS_DESC = """
    SELECT tag FROM tags ORDER BY usedAt DESC
    """

GET_MTIME = """
    SELECT bijiMTime FROM bijis WHERE filepath = :filepath
    """

GET_TAG_ATIME = """
    SELECT usedAt FROM tags WHERE tag = :tag
    """

GET_ALL_FILEPATHS = """
    SELECT filepath FROM bijis
    """

DELETE_BIJI = """
    DELETE FROM bijis WHERE filepath = :filepath
    """


class BijiDatabase:

    db: sqlite3.Connection

    @staticmethod
    def create_db() -> None:
        db_path = Path(DB_NAME)

        if db_path.exists():
            raise FileExistsError(f'The file exists: {db_path}')

        conn = sqlite3.connect(DB_NAME)
        conn.executescript(CREATE_TABLES)
        conn.commit()
        conn.close()

    @classmethod
    def connect_db(cls) -> None:
        db_path = Path(DB_NAME)

        if not db_path.exists():
            raise FileNotFoundError(f'Not Found: {db_path}')

        cls.db = sqlite3.connect(DB_NAME)
        cls.db.row_factory = sqlite3.Row
        cls.db.execute('PRAGMA foreign_keys = ON')

    @classmethod
    def commit(cls) -> None:
        cls.db.commit()

    @classmethod
    def close_db(cls) -> None:
        cls.db.close()

    @classmethod
    def update_biji(cls, biji_dict) -> None:
        cls.db.execute(UPDATE_BIJI, biji_dict)

    @classmethod
    def update_tag_time(cls, tag: str) -> None:
        used_at = datetime.now().isoformat()
        cls.db.execute(UPDATE_TAG_TIME, dict(tag=tag, usedAt=used_at))

    @classmethod
    def update_biji_mtime(cls, filepath: str, mtime: str) -> None:
        cls.db.execute(UPDATE_BIJI_MTIME, dict(filepath=filepath,
                                               bijiMTime=mtime))
        cls.db.commit()

    @classmethod
    def unlink_tag(cls, tag: str, filepath: str) -> None:
        cls.db.execute(UNLINK_TAG, dict(tag=tag, filepath=filepath))
        cls.update_tag_time(tag)

    @classmethod
    def insert_to_tag_biji(cls, tag: str, filepath: str) -> None:
        cls.db.execute(INSERT_INTO_TAG_BIJI, dict(tag=tag, filepath=filepath))
        cls.update_tag_time(tag)

    @classmethod
    def insert_to_tags(cls, tags: Set[str]) -> None:
        """ Inserts into the 'tags' table, ignore if the tag exists. """
        used_at = datetime.now().isoformat()
        for tag in tags:
            if not cls.get_tag_atime(tag):
                cls.db.execute(INSERT_INTO_TAGS, dict(tag=tag, usedAt=used_at))

    @classmethod
    def get_tag_atime(cls, tag: str) -> str:
        """
        To check if a tag exists,
        return an empty string if it doesn't exists.
        """
        result: sqlite3.Row = cls.db.execute(
            GET_TAG_ATIME, dict(tag=tag)).fetchone()
        if result:
            return result['usedAt']
        else:
            return ''

    @classmethod
    def get_tags(cls, filepath: str) -> Set[str]:
        tags = set()
        cur = cls.db.execute(GET_TAGS, dict(filepath=filepath))
        for row in cur:
            tags.add(row['tag'])
        return tags

    @classmethod
    def get_bijis(cls, tag: str) -> Set[str]:
        bijis = set()
        for row in cls.db.execute(GET_BIJIS, dict(tag=tag)):
            bijis.add(row['filepath'])
        return bijis

    @classmethod
    def insert_to_bijis(cls, biji_dict: dict) -> None:
        cls.db.execute(INSERT_INTO_BIJIS, biji_dict)

    @classmethod
    def get_mtime(cls, filepath: str) -> str:
        """
        Use bijiMTime to check if an record exists,
        return an empty string if it does not exist.
        """
        result: sqlite3.Row = cls.db.execute(
            GET_MTIME, dict(filepath=filepath)).fetchone()
        if result:
            return result['bijiMTime']
        else:
            return ''

    @classmethod
    def get_all_filepaths(cls) -> sqlite3.Cursor:
        return cls.db.execute(GET_ALL_FILEPATHS)

    @classmethod
    def delete_biji(cls, filepath: str) -> None:
        cls.db.execute(DELETE_BIJI, dict(filepath=filepath))
        cls.db.commit()

    @classmethod
    def get_all_tags_desc(cls) -> sqlite3.Cursor:
        return cls.db.execute(GET_ALL_TAGS_DESC)

    # @classmethod
    # def get_tags_order_by_tag(cls) -> List[Tuple[str, int]]:
    #     result = []
    #     for row in cls.db.execute(GET_TAGS_ORDER_BY_TAG):
    #         result.append((row['tag'], row['count']))
    #     return result

    @classmethod
    def get_tags_order_by_tag(cls) -> sqlite3.Cursor:
        return cls.db.execute(GET_TAGS_ORDER_BY_TAG)

    @classmethod
    def get_tags_order_by_count(cls) -> List[Tuple[str, int]]:
        result = cls.get_tags_not_used()
        for row in cls.db.execute(GET_TAGS_ORDER_BY_COUNT):
            result.append((row['tag'], row['count']))
        return result

    @classmethod
    def get_tags_order_by_time(cls) -> sqlite3.Cursor:
        return cls.db.execute(GET_TAGS_ORDER_BY_TIME)

    @classmethod
    def get_tags_not_used(cls) -> List[Tuple[str, int]]:
        result = []
        for row in cls.db.execute(GET_TAGS_NOT_USED):
            result.append((row['tag'], 0))
        return result

    @classmethod
    def delete_tag(cls, tag: str) -> None:
        cls.db.execute(DELETE_TAG, dict(tag=tag))

    @classmethod
    def update_tag(cls, old_tag: str, new_tag: str) -> None:
        cls.db.execute(UPDATE_TAG, dict(old=old_tag, new=new_tag))
        cls.db.commit()
