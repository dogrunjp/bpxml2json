# -*- coding: utf-8 -*-
import json
from datetime import datetime, date


def dict2jsnl(dct, data_type, output_f):
    """
    XMLから変換したdictをElasticSearcchにバルクインポートするためのjsonl形式のファイルに整形して書き出す。
    xml2jsonからelementごとに随時ファイルに書き出しを行う
    :param data_type: BioProject等. ElasticSearchのインデックス名となる
    :param dct: XMLからdictに変換したBioProjectのレコード
    :param output_f:
    :return:
    """
    # 追記するのでモードで"a"を指定する
    writer = open(output_f, "a")
    obj = {data_type: dct}
    acc = dct["identifier"]

    h = json.dumps({"index": {"_index": data_type, "_type": "metadata", "_id": acc}})
    writer.write(h)
    writer.write("\n")

    m = json.dumps(obj, default=json_serial)
    writer.write(m)
    writer.write("\n")

    writer.close()


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

