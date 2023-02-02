# bpxml2json

bioproject.xmlをDDBJハッシュテーブルの項目に合わせたJSONに変換するユーティリティです。

## 使い方と実施結果

開発途中のため読み込み・書き出しパスはxml2json.pyにハードコード（103行目）したままです。

```
$ time python xml2json.py                                                      

real    2m30.532s
user    2m25.071s
sys     0m5.159s

```

701,512 要素を含む817MのJSONが書き出されました（2023/1/31）
