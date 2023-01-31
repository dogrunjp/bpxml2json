# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xmltodict
import json
import datetime
from lxml import etree

import xmlutils
import defaultdictvals


BIOPROJECT_CONF = {
    "ftp_url": "ftp.ncbi.nlm.nih.gov",
    "ftp_file_path": "bioproject",

}


def xml2json(xml_str, output_path):
    json_doc = xmltodict.parse(xml_str, dict_constructor=dict, force_cdata=True, cdata_key='$')
    return json.dumps(json_doc)


def save_json(json_str, output_path):
    with open(output_path) as f:
        json.dump(json_str, f, indent=2, ensure_ascii=False)


def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def bioproject_xml_to_dict(file_path:str, output_path:str):
    """
    bioproject.xmlのうち設定された要素をフラットなxmlとしてJSONに変換して書き出す
    :param file_path: bioproject.xmlのパス
    :param output_path: 書き出すJSONファイル名
    :return: void
    """
    # Todo: DDBJ のBioProjectのハッシュテーブルの要素を追加する
    context = etree.iterparse(file_path, tag="Package", recover=True)
    dd = defaultdictvals.DefaultDictVal()

    i = 0
    docs = []
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["type"] = "bioproject"
            doc["identifier"] = dd.get_xattr(element, ".//ProjectID/ArchiveID/@accession")
            doc["organism"] = dd.get_value(element, ".//Project/Project/ProjectDescr/Name")
            doc["title"] = dd.get_value(element, ".//Project/Project/ProjectDescr/Title")
            doc["description"] = dd.get_value(element, ".//Project/ProjectDescr/Description")
            doc["data type"] = dd.get_value(element, ".//ProjectTypeSubmission/ProjectDataTypeSet/DataType")
            doc["organization"] = dd.get_value(element, ".//Submission/Description/Organization/Name")
            doc["publication"] = dd.get_publications(element, ".//Project/ProjectDescr/Publication")
            doc["properties"] = None
            doc["dbXrefs"] = dd.get_xattrs(element, ".//Project/ProjectDescr/LocusTagPrefix/@biosample_id")
            doc["distribution"] = None
            doc["Download"] = None
            doc["status"] = dd.get_value(element, ".//Submission/Description/Access")
            doc["visibility"] = None
            doc["dateCreated"] = dd.get_xattr(element, ".//Submission/@submitted")
            doc["dateModified"] = dd.get_xattr(element, ".//Submission/@last_update")
            doc["datePublished"] = dd.get_value(element, ".//Project/ProjectDescr/ProjectReleaseDate ")

            # そのままxmltodictで機械的にJSONに変換したい場合以下を実行すしリストに追加する
            # ただしxmlが部分的にでもマルフォームであった場合エラーが発生する
            # xml_str = etree.tostring(element)
            # metadata = xml2json(xml_str)
            docs.append(doc)

        try:
            clear_element(element)
        except TypeError:
            pass
        '''
        # for test 
        if i > 10:
            res = {"bioproject": docs}
            with open(output_path, "w") as f:
                json.dump(res, f, indent=4)

            break
        '''
    with open(output_path, "w") as f:
        json.dump(docs, f, indent=4)


def bioproject_xml_to_json(file_path: str, output_path:str):
    """
    bioproject.xmlを機械的に階層構造を保ったままJSONに変換して書き出す
    :param file_path:
    :param output_path:
    :return:
    """
    root = xmlutils.read_xml_string(file_path)
    xml2json(root, output_path)


def study(p,f):
    """
    Studyでの例
    etreeのxpathの切り方の参考に
    :param p:
    :param f:
    :return:
    """
    context = etree.iterparse(f, tag="STUDY")
    dd = DefaultDictVal()
    for events, element in context:
        if element.tag == "STUDY":
            uid = dd.get_attr(element, "accession")
            vals = {}
            vals["prefix"] = p
            vals["type"] = "study"
            vals["uid"] = uid
            vals["center_name"] = dd.get_attr(element, "center_name")
            vals["center_project_name"] = dd.get_value(element, ".//DESCRIPTOR/CENTER_PROJECT_NAME")
            vals["study_title"] = dd.get_value(element, ".//DESCRIPTOR/STUDY_TITLE")
            vals["publication_id"] = dd.get_vals(element, ".//STUDY_LINK/XREF_LINK/ID")
            vals["study_link_url"] = dd.get_vals(element, ".//STUDY_LINK/URL_LINK/URL")
            vals["abstract"] = dd.get_vals(element, ".//DESCRIPTOR/STUDY_ABSTRACT")
            vals["study_type"] = dd.get_xattr(element, ".//DESCRIPTOR/STUDY_TYPE/@existing_study_type")
            eids = element.findall(".//IDENTIFIERS/EXTERNAL_ID")
            ids = list(set([x.text for x in eids]))
            ids.append(vals["uid"])
            vals["id"] = list(set(ids))

            xml_str = etree.tostring(element)
            metadata = xml2json(xml_str)
            #putdata = PutData()
            putmetadata.putvalues(vals, metadata)
            clear_element(element)


if __name__ == "__main__":
    bioproject_xml_to_dict("/mnt/sra/xml/bioproject.xml", "test_json.json")
