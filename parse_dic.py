# parse_dic.py
# parse the macab-format dictinary and insert to DB the data.
# python parse_dic.py dicpath dicID dicencoding dbpath

import sys
import sqlite3
import logging

def main(dicpath, dicID, encoding, dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()

    dic_type = dicID
    with open(dicpath, "r", encoding=encoding) as f:
        while(f.readable()):
            origin = f.readline()
            if(len(origin)==0): break # 終端
            cols = origin.split(",")
            surface = cols[0]
            kana = cols[11]
            firstChar, endChar = get_edge_kana(kana)        
            try:
                c.execute(
                    "insert into words (surface, kana, firstChar, endChar, dicType, origin) values (?,?,?,?,?,?)",
                    (surface, kana, firstChar, endChar, dic_type, origin)
                )
                logging.info(f"{surface}：{firstChar}～{endChar}")
            except:
                # PRIMARY KEYがだぶったとき
                pass
    # 余計なものを消す
    c.execute("delete from words where length(kana)=1 and endChar=firstChar and kana=surface;")
    c.execute("delete from words where length(kana)=2 and dicType=7 and endChar=firstChar and kana=surface;")
    for komoji in "ァィゥェォヵヶッヮャュョ":
        c.execute("delete from words where kana=?;", komoji)
    c.execute("delete from words where kana=?;","㋘")
    c.execute("delete from words where endChar=?;","Ａ")
    c.execute("delete from words where endChar=?;","う")
    c.execute("delete from words where endChar=?;","Ｑ")
    c.execute("delete from words where endChar=?;","ｂ")

    conn.commit()
    conn.close()

def get_edge_kana(kana):
    firstChar = kana[0]
    for c in kana[1:]:
        if (c not in "ァィゥェォヵヶャュョヮー"):
            break
        else:
            firstChar += c

    endChar = ""
    for c in reversed(kana):
        endChar = c + endChar
        if (c not in "ァィゥェォヵヶャュョヮー"):
            break

    return firstChar, endChar


if __name__=="__main__":
    logging.basicConfig()
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(f"{sys.argv[1]} is done.")