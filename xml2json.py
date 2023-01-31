# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xmltodict
import json
import datetime
from lxml import etree


BIOPROJECT_CONF = {
    "ftp_url": "ftp.ncbi.nlm.nih.gov",
    "ftp_file_path": "bioproject",

}

def xml2json(xml_str):
    json_doc = xmltodict.parse(xml_str, dict_constructor=dict, force_cdata=True, cdata_key='$')
    return json.dumps(json_doc)


def clear_element(element):
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def save_metadata():
    # Todo: DDBJ のBioProjectのハッシュテーブルの要素を追加する
    target_file = "/".join([BIOPROJECT_CONF["local_file_path"], BIOPROJECT_CONF["xml_file_name"]])
    context = etree.iterparse(target_file, tag="Package")

    i = 0
    docs = []
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["identifier"] = element.find(".//Project/Project/ProjectID/ArchiveID").attrib["accession"]
            # Todo: ESは"_id"が設定されている必要があるはず
            xml_str = etree.tostring(element)
            metadata = xml2json(xml_str)
            doc["metadata"] = metadata
            doc["submit_date"] = datetime.datetime.today()
            docs.append(doc)
            i += 1

        clear_element(element)
        # 以下mongoを使った場合のchunk処理
        """
        if i > 1000:
            i = 0
            db_connect[target_db].insert_many(docs)
            docs = []
        """

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
