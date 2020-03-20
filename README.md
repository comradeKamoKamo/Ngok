# Ngok - Ngok is the Gear of *Kotoba-asobi*.
　Ngokはしりとりを研究し、最強のしりとり戦術やしりとりAIを作ることを目的としているお遊びリポジトリです。正直、他人に見せるものではないと思います。
# 単語の分析
　そもそも日本語の単語には、先頭にきやすい文字や終端にきやすい文字があるはずです。辞書データを用いてそれを分析します。
## 辞書準備
　MeCab用の辞書を利用します。IPA辞書と、[mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)を中の人は使いました。しりとりは名詞しか使えませんから、名詞(Noun)とかかれた辞書ファイルを使うと良いでしょう。neologdはseedディレクトリの中のファイルを解答すると生辞書です。  
 はじめに、NgokではSQLiteで単語データを管理するので```data/db_init.sql```からDBを作成します。dicTypesテーブルにはどの辞書ファイルを利用したかを書き込んでおくと便利です。
```
INSERT INTO dicTypes VALUES(1,'IPADIC Noun.csv 名詞一般');
INSERT INTO dicTypes VALUES(2,'IPADIC Noun.adverbal.csv 名詞副詞可能');
INSERT INTO dicTypes VALUES(3,'IPADIC Noun.org.csv 名詞固有名詞組織');
INSERT INTO dicTypes VALUES(4,'IPADIC Noun.place.csv 名詞固有名詞地域一般');
INSERT INTO dicTypes VALUES(5,'IPADIC Noun.proper.csv 名詞固有名詞一般');
INSERT INTO dicTypes VALUES(6,'IPADIC Noun.verbal.csv 名詞サ変接続');
INSERT INTO dicTypes VALUES(7,'IPADIC Symbol.csv 記号');
INSERT INTO dicTypes VALUES(100,'mecab-ipadic-NEologd mecab-user-dict-seed.20200130.csv');
```
中の人はこのように登録しています。  
　```parse.dic.py```は辞書データをDBに書き込みます。  
 `python parse_dict.py dicpath dicID dicencoding dbpath`  
 dicIDはその辞書データがdicTypesテーブルで何番か、ということです。中の人と同じにするには、辞書データを```data```下に保存して```dic2db.sh```を使うといいかもしれません。IPA辞書はEUC-JP、NEologdはUTF-8である点に注意してください。
## 始まりと終わりを数える
　Xで始まりYで終わる単語はいくつか？を得ましょう。ヨミガナが同じ語は二度と使えないルールとします。  
 `python words_analyze.py dbpath mode`  
 ```mode```にはしりとりのルールを指定します。
 ```
 # モードは各オプションの積で指定します。
    # 何も指定しない場合、厳密に一致する必要があります。    
    # 相互交換可能オプション
    # 2 濁点<=>濁点              e.g.)帝国=>軍事法廷
    # 3 半濁点<=>濁点            e.g.)法被=>広島
    # 小文字に関するオプションは併用不可です。
    # 何も指定しない場合は、自動車=>社宅のようになります。
    # 5 小文字<=>標準文字        e.g.)自動車=>ヤクザ               
    # 7 小文字を除く             e.g.)自動車=>指紋
    # 11 小文字は負け            e.g.)自動車（負け）
    # 13 （予約）
    # 長音のルールも併用不可です。何も指定しないと、マヨラー=>ラーメンのようになります。
    # 17 長音は省く              e.g.)メーデー=>デビルマン
    # 19 長音は母音を取る        e.g.)メーデー=>エンブレム
    # 23 長音は負け              e.g.)メーデー（負け）
    # 29 （予約）
    # その他のルール
    # 31 「ン」で負けにしない。  e.g.)食パン=>ンゴック族
    # 37 ジ<=>ヂ                 e.g.)鼻血=>ジルコニウム
    # 41 ズ<=>ヅ                 e.g.)木更津=>ずんだ餅
    # 43 ヲ<=>オ                 e.g.)みつを。=>折り紙
# 推奨は2*3*5*17*43です。
```
実行する前に、先程のDBにインデックスを作成しましょう。日が暮れます。  
``` CREATE INDEX my_index on words(substr(firstChar,1,1),endChar); ```  
また、```words_analyze.py```はマルチスレッドで操作しますが、8プロセスに設定されていますので、高性能なCPUの方は書き換えると早くなります。  
　`cm.npy`と`endList.pickle`が出力されます。前者は`[始端文字のインデックス,終端文字のインデックス]`で単語数が得られます。後者は少しややこしく、文字種の長さのリストで（.npyのインデックスはこのリストのインデックスと一緒）。各要素の`[0]`に「文字セット」`[1]`に「実際の終端型リスト」が入っています。意味がわからないと思います。説明力がないのでなんとも言えません。
# 可視化
```data_plot.py```はデータを可視化します。推奨モードで実行したサンプルを示します。  
![cm](https://github.com/comradeKamoKamo/Ngok/blob/dev/output_21930/cm.png?raw=true)
![rate](https://github.com/comradeKamoKamo/Ngok/blob/dev/output_21930/rate.png?raw=true)
単語終始比率とは「ある文字Xについて、Xで終わる単語数÷Xで始まる単語数」です。高いほど＊攻めをする勝ちがあると言えます。る攻めの強さは科学的な裏打ちがあります。
