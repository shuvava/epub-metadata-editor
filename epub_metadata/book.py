import logging
import os
import tempfile
import zipfile
from typing import Optional, List

from lxml import etree
from .file import read_epub_metadata
from .epub import (
    find_metadata_items,
    get_metadata_main, get_metadata_ext,
    get_metadata_node,
    get_book_sequence,
)


class Book:
    def __init__(self, fname: str, log: logging.Logger):
        self._file = fname
        self._log = log
        self._tree = read_epub_metadata(fname)
        self._metadata = None
        self._metadata = get_metadata_node(self._tree)
        series, num = get_book_sequence(self._tree, self._metadata)
        self._series = series
        self._series_num = num
        for el in self._metadata:
            if 'title' in el.tag:
                self._title = el
            if 'creator' in el.tag:
                self._creator = el
            if 'language' in el.tag:
                self._language = el
            if 'identifier' in el.tag:
                self._identifier = el

    @property
    def title(self) -> str:
        return self._title.text

    @title.setter
    def title(self, title):
        self._title.text = title

    @property
    def creator(self) -> str:
        return self._creator.text

    @creator.setter
    def creator(self, title):
        self._creator.text = title

    @property
    def series(self) -> str:
        return self._series

    @property
    def series_num(self) -> int:
        return self._series_num

    def get_metadata(self, key: str, ns: str = None) -> List:
        return find_metadata_items(self._tree, self._metadata, key, ns)

    def get_dc(self, key: str) -> Optional[str]:
        return get_metadata_main(self._tree, self._metadata, key)

    def get_meta(self, key: str) -> Optional[str]:
        return get_metadata_ext(self._tree, self._metadata, key)

    def update(self):
        self._log.debug(f'file "{self._file}" updating')
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self._file))
        os.close(tmpfd)
        with zipfile.ZipFile(self._file, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:
                zout.comment = zin.comment  # preserve the comment
                for item in zin.infolist():
                    content = zin.read(item.filename)
                    if 'content.opf' in item.filename:
                        content = etree.tostring(self._tree,
                                                 pretty_print=True, encoding='utf-8', xml_declaration=False,
                                                 doctype='<?xml version="1.0" encoding="UTF-8"?>')
                    zout.writestr(item, content)
        # replace with the temp archive
        os.remove(self._file)
        os.rename(tmpname, self._file)

    def __repr__(self):
        return f"<Book(creator='{self.creator}', title='{self.title}')>"
