# 依存関係ライブラリのinstall等について


## ubuntuのRubyのバージョンを3.2.2に変更する

- rbenvをインストール
- ruby 3.2.2をインストール（rbenv install 3.2.2）
- rubyバージョンを3.2.2に変更（rbenv global 3.2.2）

## oxのインストールとgemfileの実行

- xmlのパーサーはox（https://github.com/ohler55/ox）　を使用する(rexmlは遅いため)
- rubyのxmlパーサーの速さについては例えばこんな記事もある（https://new-pill.hatenablog.com/entry/2017/05/06/215945）
- gem install ox
- bundle install
- bundle install