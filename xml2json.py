# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET


BIOPROJECT_CONF = {
    "ftp_url": "ftp.ncbi.nlm.nih.gov",
    "ftp_file_path": "bioproject",
    "xml_file_name": "bioproject.xml",
    "local_file_path": "/home/ubuntu/data",
    "solr_path": "http://localhost:8983/solr/bioproject/",
    "dih_path": "http://localhost:8983/solr/bioproject/dataimport"
}


def save_metadata():
    target_file = "/".join([BIOPROJECT_CONF["local_file_path"], BIOPROJECT_CONF["xml_file_name"]])
    context = etree.iterparse(target_file, tag="Package")

    target_db = DB_CONF["metadata"]["bioproject_tmp"]
    i = 0
    docs = []
    for events, element in context:
        if element.tag == "Package":
            doc = {}
            doc["_id"] = element.find(".//Project/Project/ProjectID/ArchiveID").attrib["accession"]
            xml_str = etree.tostring(element)
            metadata = xml2json(xml_str)
            doc["metadata"] = metadata
            doc["submit_date"] = datetime.datetime.today()
            docs.append(doc)
            i += 1

        clear_element(element)
        if i > 1000:
            i = 0
            db_connect[target_db].insert_many(docs)
            docs = []
