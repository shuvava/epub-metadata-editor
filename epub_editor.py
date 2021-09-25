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
import sys
from pathlib import Path
from shutil import copyfile
from typing import List

from epub_metadata import Book


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
