from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Tuple, Set

from ..bijidb.bijidatabase import BijiDatabase


# noinspection PyPep8Naming
class Biji:
    _filepath: str
    _filename: str
    _suffix: str
    _mimetype: str
    _filesize: int
    _updatedAt: str
    _backupAt: str
    _bijiCTime: str
    _bijiMTime: str
    _tags: Tuple[str]
    _fields: Tuple[str] = ('filepath',
                           'filename',
                           'suffix',
                           'mimetype',
                           'filesize',
                           'updatedAt',
                           'backupAt',
                           'bijiCTime',
                           'bijiMTime',
                           'tags')

    def __init__(self, filepath: str, tags: Tuple[str] = ()) -> None:
        file_path = Path(filepath)
        filestat = file_path.lstat()
        now = datetime.now().isoformat()

        self._filepath = filepath
        self._filename = file_path.name
        self._suffix = file_path.suffix.lower()
        self._mimetype = mimetypes.guess_type(filepath, strict=False)[0]
        self._filesize = filestat.st_size
        self._updatedAt = datetime.fromtimestamp(filestat.st_mtime).isoformat()
        self._backupAt = ''
        self._bijiCTime = now
        self._bijiMTime = now
        self._tags = tags

        self.biji_json_path = self.get_biji_json_path(filepath)
        self.db = BijiDatabase

        try:
            self.db.connect_db()
        except FileNotFoundError:
            self.db.create_db()
            self.db.connect_db()

    @staticmethod
    def get_biji_json_path(filepath: str) -> Path:
        return Path(f'{filepath}.biji.json')

    @classmethod
    def update_tags_for_files(cls,
                              files: Set[str],
                              deleted_tags: Set[str],
                              new_added_tags: Set[str]):
        """
        Updates tags for files.
        Creates the '.biji.json' file if it does not exist.
        Inserts a new record if it does not exist in the database.
        """
        for file in files:
            biji_json_path = cls.get_biji_json_path(file)

            if biji_json_path.exists():
                biji = cls.from_file(file)
            else:
                biji = cls(file)

            tags = set(biji.tags) - deleted_tags | new_added_tags
            if tags != set(biji.tags):
                biji.tags = tags
                biji.write_file()

            bijiMTime = biji.get_mtime_from_db()
            if not bijiMTime:
                biji.insert_biji_and_tags_to_db()
            elif biji._bijiMTime > bijiMTime:
                biji.update_biji_and_tags_to_db()

    @classmethod
    def from_file(cls, filepath: str) -> Biji:  # noqa:F821
        biji_json_path = cls.get_biji_json_path(filepath)
        biji_json = biji_json_path.read_text(encoding='utf-8')
        biji_dict: dict = json.loads(biji_json)
        biji = cls(filepath)

        for field in cls._fields:
            if field in biji_dict:
                biji.__dict__[f'_{field}'] = biji_dict[field]

        if biji._filepath != filepath:
            biji._filepath = filepath
            biji.write_file()
        return biji

    @property
    def tags(self) -> Tuple[str]:
        return self._tags

    @tags.setter
    def tags(self, new_tags: Tuple[str]) -> None:
        if type(new_tags) == set:
            new_tags = tuple(new_tags)
        self._tags = new_tags
        self._bijiMTime = datetime.now().isoformat()

    @property
    def bijiMTime(self) -> str:
        return self._bijiMTime

    def _asdict(self) -> dict:
        biji_dict = {}
        for field in self._fields:
            biji_dict[field] = self.__dict__[f'_{field}']
        return biji_dict

    def _asjson(self) -> str:
        return json.dumps(self._asdict(), sort_keys=True, ensure_ascii=False)

    def write_file(self) -> None:
        self.biji_json_path.write_text(self._asjson(), encoding='utf-8')

    def insert_biji_to_db(self) -> None:
        self.db.insert_to_bijis(self._asdict())
        self.db.commit()

    def insert_tags_to_db(self) -> None:
        """ Use this method only when self._filepath is new. """
        tags = set(self._tags)
        self.db.insert_to_tags(tags)
        for tag in tags:
            self.db.insert_to_tag_biji(tag, self._filepath)
        self.db.commit()

    def insert_biji_and_tags_to_db(self) -> None:
        self.insert_biji_to_db()
        self.insert_tags_to_db()

    def update_biji_to_db(self) -> None:
        """ updates the 'bijis' table, without updating the 'tags' table. """
        self.db.update_biji(self._asdict())
        self.db.commit()

    def update_tags_to_db(self) -> None:
        """
        updates the 'tag_biji' table,
        and if necessary inserts new tags to the 'tags' table.
        """
        old_tags = self.db.get_tags(self._filepath)
        for tag in old_tags:
            self.db.unlink_tag(tag, self._filepath)

        self.insert_tags_to_db()
        self.db.commit()

    def update_biji_and_tags_to_db(self):
        self.update_biji_to_db()
        self.update_tags_to_db()

    def get_mtime_from_db(self) -> str:
        """
        Use bijiMTime to check if an record exists,
        return an empty string if it does not exist.
        """
        return self.db.get_mtime(self._filepath)
