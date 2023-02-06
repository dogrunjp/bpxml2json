# -*- encoding: utf-8 -*-
import csv

def load_acc(acc_path:str) -> list:
    """
    bioproject accをファイルから読み込みリストとして返す
    :param acc_path:
    :return:
    """
    with open(acc_path, "r") as input_f:
        reader = csv.reader(input_f, delimiter='\t')
        acc = [x[0] for x in reader]
    return acc


def select_bp(pid: str, acc: list) -> bool:
    """
    accリストを利用しbioprojectの出力をフィルターする
    :return:
    """
    if pid in acc:
        return True
    else:
        return False


if __name__ == "__main__":
    acc = load_acc("/Users/oec/Desktop/data/MDB/project_acc.txt")
    for i in ["PRJNA3", "PRJNA903506","PRJEB56441"]:
        print(select_bp(i, acc))

