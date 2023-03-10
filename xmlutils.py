# -*- coding: utf-8 -*-
import xml.etree
import xml.etree.ElementTree as ET
from lxml import etree


def read_xml_string(file_path:str) -> xml:
    """
    ファイルの文字列をxmlに変換し返す
    マルフォームデータが含まれる場合エラーとなる:
    ex xml.etree.ElementTree.ParseError: mismatched tag: line 2680510, column 15
    ex xml.etree.ElementTree.ParseError: not well-formed (invalid token): line 5786791, column 71
    :param file_path:
    :return:
    """
    tree = ET.parse(file_path)
    root = tree.getroot(tree)
    return root


def bioproject_by_id(bp: xml, id:str) -> xml:
    """
    BioProjectのxmlとidを引数に指定したxmlのみ取り出すサンプル
    途中にマルフォームデータが含まれる場合エラーとなる
    :param bp:
    :param id:
    :return:
    """
    node = bp.xpath(f"//Project/Project/ProjectID/ArchiveID[@accession={id}]")
    print(node)


def find_element(file_path:str):
    """
    特定の属性を持つ要素のみ取得し書き出すサンプル
    :param file_path:
    :return:
    """
    # Todo: DDBJ のBioProjectのハッシュテーブルの要素を追加する
    context = etree.iterparse(file_path, tag="Package")
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["identifier"] = element.find(".//Project/Project/ProjectID/ArchiveID").attrib["accession"]
            # Todo: ESは"_id"が設定されている必要があるはず
            xml_str = etree.tostring(element)
            if doc["identifier"] == "PRJNA3":
                #pretty = etree.tostring(element, encoding="utf-8", pretty_print=True).decode()
                #print(pretty)
                et = etree.ElementTree(element)
                et.write('test_print', pretty_print=True)

                break

        clear_element(element)


def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def test_node_select():
    r = read_xml_string("/mnt/sra/xml/bioproject_fixed.xml")
    bioproject_by_id(r, "PRJNA3")


def test_iterparse():
    find_element("/mnt/sra/xml/bioproject.xml")


if __name__ == "__main__":
    test_iterparse()
