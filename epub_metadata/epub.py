from typing import Tuple, Iterable, List, Optional

from lxml import etree

META_FB2_SEQ = 'FB2.book-info.sequence'
META_CALIBRE_SEQ = 'calibre:series'
META_CALIBRE_INX = 'calibre:series_index'


def get_meta_item(root: etree, metadata: Iterable[object], key: str) -> List:
    """look for `key` in meta elements"""
    els = find_metadata_items(root, metadata, 'meta', None)
    return [el for el in els if key == el.attrib['name']]


def get_metadata_ext(root: etree, metadata: Iterable[object], key: str) -> Optional[str]:
    """look for `key` in meta elements and returns value if `content` attribute"""
    els = get_meta_item(root, metadata, key)
    for el in els:
        return el.attrib['content']
    return None


def get_metadata_main(root: etree, metadata: Iterable[object], key: str) -> Optional[str]:
    """find nodes in main namespace and return content of the first element"""
    els = find_metadata_items(root, metadata, key, 'dc')
    return els[0].text if len(els) > 0 else None


def find_metadata_items(root: etree, metadata: Iterable[object], key: str, ns: str = None) -> List:
    """return list of metadata(nodes) in provided namespace"""
    if ns not in root.nsmap:
        return []
    fkey = f'{{{root.nsmap[ns]}}}{key}'
    return [el for el in metadata if fkey == el.tag]


def get_metadata_node(root: etree) -> Iterable[object]:
    for el in root:
        if 'metadata' in el.tag:
            return el


def get_book_sequence(root: etree, metadata: Iterable[object]) -> Tuple[str, int]:
    """parse FB2 sequence metadata"""
    series, num = '', -1
    # try read calibre metadata
    content = get_metadata_ext(root, metadata, META_CALIBRE_SEQ)
    if content is not None:
        series = content
    content = get_metadata_ext(root, metadata, META_CALIBRE_INX)
    if content is not None:
        num = int(content)
    if num > -1:
        return series, num
    # try read fb2
    content = get_metadata_ext(root, metadata, META_FB2_SEQ)
    if content is not None:
        arr = content.split(';')
        if len(arr) == 2:
            series = arr[0]
            num = int(''.join(filter(str.isdigit, arr[1])))
            return series, num
    return series, num


def remove_book_sequence(root: etree, metadata: Iterable[object]) -> None:
    """remove sequence metadata from book xml"""
    items = get_meta_item(root, metadata, META_FB2_SEQ)
    if len(items) > 0:
        content = items[0]
        content.getparent().remove(content)
    items = get_meta_item(root, metadata, META_CALIBRE_SEQ)
    if len(items) > 0:
        content = items[0]
        content.getparent().remove(content)
    items = get_meta_item(root, metadata, META_CALIBRE_INX)
    if len(items) > 0:
        content = items[0]
        content.getparent().remove(content)


def set_book_sequence(root: etree, metadata: Iterable[object], series: str, num: int) -> None:
    """set series and series number metadata for the book"""
    remove_book_sequence(root, metadata)
    el = etree.SubElement(metadata, 'meta')
    el.attrib['name'] = META_CALIBRE_SEQ
    el.attrib['content'] = series
    el = etree.SubElement(metadata, 'meta')
    el.attrib['name'] = META_CALIBRE_INX
    el.attrib['content'] = str(num)
