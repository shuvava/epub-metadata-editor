#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (c) 2021 Vladimir Shurygin.  All rights reserved.
#
"""
Scripts updates epub files metadata looking files by provided pattern
"""
import argparse
import logging
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from shutil import copyfile
from typing import List, Optional

from lxml import etree


class Book:
    def __init__(self, fname: str, l: logging.Logger):
        self._file = fname
        self._log = l
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


def get_book_metadata(f: str):
    with zipfile.ZipFile(f, 'r') as zin:
        for item in zin.infolist():
            if 'content.opf' in item.filename:
                content = zin.read(item.filename)
                return etree.fromstring(content)


def get_args() -> argparse.Namespace:
    """create scripts arguments and parse console arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbosity',
        help='increase output verbosity',
        nargs='?', const=1, type=bool, default=False)
    parser.add_argument(
        '-f', '--files',
        help='path to epub files to update "--files=~/Documents/a*.epub"',
        required=True, nargs='?', type=str)
    parser.add_argument(
        '-b', '--backup',
        help='create backup updating files',
        nargs='?', const=1, type=bool, default=False)
    parser.add_argument(
        '-a', '--author',
        help='set author metadata "--author=\'Test Test\'"',
        nargs='?', type=str)
    parser.add_argument(
        '-t', '--title',
        help='set title metadata "--title=\'Some title\'"',
        nargs='?', type=str)

    return parser.parse_args()


def config_logger(verbose: bool) -> logging.Logger:
    """logger configuration"""
    log = logging.getLogger('epub-updater')
    log.handlers = []
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    # create formatter
    log_format = (
        '%(asctime)s - '
        '%(levelname)s - '
        '%(funcName)s - '
        '%(message)s'
    )
    formatter = logging.Formatter(log_format)
    # create console handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    # add the handler to the logger
    log.addHandler(sh)
    return log


def get_files(p: str) -> List:
    """look up files available for provided path"""
    p = Path(p).expanduser()
    return list(Path(p.parent).glob(p.name))


def main():
    args = get_args()
    logger = config_logger(args.verbosity)
    for file in get_files(args.files):
        logger.debug(f'file({str(file)})')
        book = Book(file, logger)
        logger.debug(f' DC:title {book.title}')
        logger.debug(f' DC:creator {book.creator}')
        logger.debug(f' DC:language {book.get_dc("language")}')
        logger.debug(f' DC:identifier {book.get_dc("identifier")}')
        logger.debug(f' FB2.publish-info.year {book.get_meta("FB2.publish-info.year")}')
        updated = False
        if args.author != '':
            updated = True
            book.creator = args.author
        if args.title != '':
            updated = True
            book.title = args.title
        if updated:
            if args.backup:
                bfile = Path(file.parent, f'{file.name}.bak')
                copyfile(str(file), str(bfile))
            book.update()
    logger.info('done')


if __name__ == '__main__':
    main()
