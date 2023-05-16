# bpxml2json

bioproject.xml（ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml）を
DDBJハッシュテーブルの項目に合わせた JSONに変換するユーティリティです。
ElasticSearchにbulk importするためのjsonl形式の書き出しにも対応しています。

xml2json.pyで"Package"タグごとのイテレーションし、各レコード毎の処理を行います。
xml1レコードごとに必要な要素を取得してxml2jsonl.pyに渡してjsonl line形式で書き出します。

## 使い方と実施結果（Python版）

開発途中のため読み込み・書き出しパスはxml2json.pyにハードコード（108行目）したままです。

```
$ time python xml2json.py                                                      

real    2m30.532s
user    2m25.071s
sys     0m5.159s

```

701,512 要素を含む817MのJSONが書き出されました（2023/1/31）


## 使い方（Ruby版）

### ubuntuの場合

#### 環境 
- rbenvをインストール
- rbenvで最新の3.2.2をインストール
- rbenv global 3.2.2
- gem install ox
- bundle install

#### 実行

- pathをbioprojet.xmlのパスに変更
- ruby xml2json.rb

## フルサイズのbiproject.jsonlのElasticSearchへのbulk import

- 100MBを超えるファイルをElasticSearchにbulkインポートするには、ファイルを分割してファイルごとbulk apiを実行する必要がある
- ファイルの分割と個別のインポートは bulk_import/split.sh, bulk_import/bulk_import.sh で実行できる
- split.shは50MBで分割するようにしている
