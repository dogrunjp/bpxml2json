# -*- coding: utf-8 -*-
import xml.etree
import xml.etree.ElementTree as ET
from lxml import etree


def read_xml_string(file_path:str) -> xml:
    tree = ET.parse(file_path)
    root = tree.getroot(tree)
    return root


def bioproject_by_id(bp: xml, id:str) -> xml:
    """
    BioProjectのxmlとidを引数に指定したxmlのみ取り出す
    :param bp:
    :param id:
    :return:
    """
    node = bp.xpath(f"//Project/Project/ProjectID/ArchiveID[@accession={id}]")
    print(node)


def find_element(file_path:str):
    # Todo: DDBJ のBioProjectのハッシュテーブルの要素を追加する
    context = etree.iterparse(file_path, tag="Package")
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["identifier"] = element.find(".//Project/Project/ProjectID/ArchiveID").attrib["accession"]
            # Todo: ESは"_id"が設定されている必要があるはず
            xml_str = etree.tostring(element)
            if doc["identifier"] == "PRJNA3":
                pretty = etree.tostring(element, encoding="utf-8", pretty_print=True).decode()
                print(pretty)
                # ファイルに書き出す場合
                et = etree.ElementTree(element)
                et.write('test_print', pretty_print=True)
            break

        clear_element(element)


def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def test_node_select():
    r = read_xml_string("bioproject.xml")
    bioproject_by_id(r, "PRJNA3")


def test_iterparse():
    find_element("/mnt/sra/xml/bioproject.xml")


if __name__ == "__main__":
    test_node_select()
