import zipfile

from lxml import etree


def read_epub_metadata(f: str) -> etree:
    """read XML from 'content.opf' file in epub zip archive"""
    with zipfile.ZipFile(f, 'r') as zin:
        for item in zin.infolist():
            if 'content.opf' in item.filename:
                content = zin.read(item.filename)
                return etree.fromstring(content)
