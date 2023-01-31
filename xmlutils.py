# -*- coding: utf-8 -*-
import xml.etree
import xml.etree.ElementTree as ET


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


def test_node_select():
    r = read_xml_string("bioproject.xml")
    bioproject_by_id(r, "PRJNA3")


if __name__ == "__main__":
    test_node_select()
