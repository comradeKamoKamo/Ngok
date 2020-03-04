CREATE TABLE [words] (
[surface] TEXT, --辞書に登録されている単語そのもの
[kana] TEXT, --単語のヨミガナ。全角カタカナ
[firstChar] TEXT, --始まりのカナ
[endChar] TEXT, --終わりのカナ
[dicType] INTEGER, --辞書種。別テーブル参照。
[origin] TEXT, --辞書のデータを保持しておく欄
PRIMARY KEY([surface])
);
CREATE TABLE [dicTypes] (
[ID] INTEGER, --辞書ID
[Name] TEXT, --辞書名
PRIMARY KEY([ID])
);