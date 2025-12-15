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
from shutil import copyfile, move
from typing import List

from transliterate import translit, get_available_language_codes

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
    parser.add_argument('-s', '--series', help='set series metadata', nargs='?', type=str)
    parser.add_argument(
        '-n', '--num', help='set series number metadata', nargs='?', type=int, default=-1
    )
    parser.add_argument(
        '-r', '--rename',
        help='rename file name to book-series_book-series-num.epub',
        nargs='?', const=1, type=bool, default=False)
    parser.add_argument('--auto-series', metavar='auto_series', help='auto-generate series metadata from file name',
                        nargs='?', const=1, type=bool, default=False)

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
    """look up files available for a provided path"""
    p = Path(p).expanduser()
    files = list(Path(p.parent).glob(p.name))
    return sorted(files, key=lambda f: f.name)


def main():
    args = get_args()
    logger = config_logger(args.verbosity)
    cnt = 1
    for file in get_files(args.files):
        logger.debug(f'file({str(file)})')
        book = Book(file, logger)
        logger.debug(f' DC:title \'{book.title}\'')
        logger.debug(f' DC:creator \'{book.creator}\'')
        logger.debug(f' DC:language {book.language}')
        logger.debug(f' DC:identifier {book.get_dc("identifier")}')
        logger.debug(f' FB2.publish-info.year {book.get_meta("FB2.publish-info.year")}')
        logger.debug(f' series \'{book.series}:{book.series_num}\'')
        updated = False
        if args.author is not None:
            updated = True
            book.creator = args.author
        if args.title is not None:
            updated = True
            book.title = args.title
        if args.series is not None:
            updated = True
            book.series = args.series
        if args.num >= 0:
            updated = True
            book.series_num = args.num
        if args.auto_series:
            updated = True
            book.title = f'{book.title}  {cnt:02d}'
            book.series_num = cnt
        if updated:
            if args.backup:
                bfile = Path(file.parent, f'{file.name}.bak')
                copyfile(str(file), str(bfile))
            book.update()
            if args.rename:
                # fixup series metadata
                book.series = book.series
                if book.language in get_available_language_codes():
                    btitile = translit(book.series, book.language, reversed=True) \
                        .replace(' ', '_') \
                        .replace('\'', '')
                    new_fname = f'{btitile}_{book.series_num}.epub'
                    bfile = Path(file.parent, new_fname)
                    move(str(file), str(bfile))
        cnt += 1
    logger.info('done')


if __name__ == '__main__':
    main()
