import logging
import os
import tempfile
import zipfile
from typing import Optional, List

from lxml import etree
from .reader import get_book_metadata


class Book:
    def __init__(self, fname: str, log: logging.Logger):
        self._file = fname
        self._log = log
        self._tree = get_book_metadata(fname)
        self._metadata = None
        for el in self._tree:
            if 'metadata' in el.tag:
                self._metadata = el
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
    def title(self):
        return self._title.text

    @title.setter
    def title(self, title):
        self._title.text = title

    @property
    def creator(self):
        return self._creator.text

    @creator.setter
    def creator(self, title):
        self._creator.text = title

    def get_metadata(self, key: str, ns: str = None) -> List:
        if ns not in self._tree.nsmap:
            return []
        fkey = f'{{{self._tree.nsmap[ns]}}}{key}'
        return [el for el in self._metadata if fkey == el.tag]

    def get_dc(self, key: str) -> Optional[str]:
        els = self.get_metadata(key, 'dc')
        el = els
        return el[0].text if len(el) > 0 else None

    def get_meta(self, key: str):
        els = self.get_metadata('meta', None)
        for el in els:
            if key == el.attrib['name']:
                return el.attrib['content']

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
