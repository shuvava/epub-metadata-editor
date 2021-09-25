import zipfile

from lxml import etree


def get_book_metadata(f: str):
    with zipfile.ZipFile(f, 'r') as zin:
        for item in zin.infolist():
            if 'content.opf' in item.filename:
                content = zin.read(item.filename)
                return etree.fromstring(content)