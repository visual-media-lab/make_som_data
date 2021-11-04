# make_som_data
書籍「[自己組織化マップとその応用](https://www.maruzen-publishing.co.jp/item/?book_no=294607)」に同包されているソフト用の入力データファイルを作る
#使い方
## 最初にやること
mecabのインストールを最初に行ってください.  
インストール方法↓  
[ubuntu](https://qiita.com/ekzemplaro/items/c98c7f6698f130b55d53)  
[windows](https://qiita.com/menon/items/f041b7c46543f38f78f7) (Anacondaが推奨されていますがこのためにわざわざAnacondaを入れなくてもいいと思います)
## 使い方
`config.yaml`を編集して設定後以下のコマンドを実行してください.
```
~$ pip3 install -r requirements.txt
~$ python3 make_som_data.py
```
