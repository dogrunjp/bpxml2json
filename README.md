# bpxml2json

bioproject.xml（ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml）をDDBJハッシュテーブルの項目に合わせたJSONに変換するユーティリティです。
ElasticSearchにbulk importするためのjsonl形式の書き出しにも対応しています。

xml2json.pyでxml1レコードごとに必要な要素を取得してxml2jsonl.pyに渡してjsonl line形式で書き出します。

## 使い方と実施結果

開発途中のため読み込み・書き出しパスはxml2json.pyにハードコード（108行目）したままです。

```
$ time python xml2json.py                                                      

real    2m30.532s
user    2m25.071s
sys     0m5.159s

```

701,512 要素を含む817MのJSONが書き出されました（2023/1/31）
