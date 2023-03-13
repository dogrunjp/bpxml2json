# -*- coding: utf-8 -*-
import xmltodict
import json
from lxml import etree

import xmlutils
import defaultdictvals
import xml2jsonl
import select_by_acc


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

    # bioproject accのリストによるfilterを追加する場合
    acc = select_by_acc.load_acc()

    context = etree.iterparse(file_path, tag="Package", recover=True)
    dd = defaultdictvals.DefaultDictVal()
    # i = 0
    docs = []
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["type"] = "bioproject"
            doc["identifier"] = dd.get_xattr(element, ".//ProjectID/ArchiveID/@accession")

            # accリストに存在する要素のみ書き出したい場合
            if select_by_acc.select_bp(doc["identifier"], acc):

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
                # Todo: 以下ElasticSearchの項目がDate型なため空の値を登録できない（レコードのインポートがエラーとなりスキップされる）
                date_created = dd.get_xattr(element, ".//Submission/@submitted")
                if date_created: doc["dateCreated"] = date_created
                date_mmodified = dd.get_xattr(element, ".//Submission/@last_update")
                if date_mmodified: doc["dateModified"] = date_mmodified
                date_published = dd.get_value(element, ".//Project/ProjectDescr/ProjectReleaseDate")
                if date_published: doc["datePublished"] = date_published

                # そのままxmltodictで機械的にJSONに変換したい場合以下を実行すしリストに追加する
                # ただしxmlが部分的にでもマルフォームであった場合エラーが発生する
                # xml_str = etree.tostring(element)
                # metadata = xml2json(xml_str)
                # docs.append(doc)

                # 特定の要素のみ取り出したい場合
                # if doc["identifier"] == "":
                    #docs.append(doc)

                # jsonlを書き出す場合
                xml2jsonl.dict2jsnl(doc, "bioproject", f"{output_path}l")

        try:
            clear_element(element)
        except TypeError:
            pass

        '''
        if i > 10:
            res = {"bioproject": docs}
            write_json(output_path, docs)
            break
        i += 1
        '''
    # JSONを書き出す場合
    # write_json(output_path, docs)


def bioproject_xml_to_json(file_path: str, output_path:str):
    """
    bioproject.xmlを機械的に階層構造を保ったままJSONに変換して書き出す
    :param file_path:
    :param output_path:
    :return:
    """
    root = xmlutils.read_xml_string(file_path)
    xml2json(root, output_path)


def write_json(out_path:str, docs: dict):
    with open(out_path, "w") as f:
        json.dump(docs, f, indent=4)


if __name__ == "__main__":
    bioproject_xml_to_dict("bioproject.xml", "bioproject.json")
