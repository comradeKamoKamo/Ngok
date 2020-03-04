# python words_analyze.py dbpath mode
# 単語セットを分析します。modeはしりとりルールを指定します。
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
    # 43 を<=>お                 e.g.)みつを。=>折り紙
# 推奨は2*3*5*17*43です。


import sys
import copy
import sqlite3
import pickle
from multiprocessing import Pool
import numpy as np

def main(dbpath, mode):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    
    # 終端文字が何通りあるか調べる
    c.execute("select distinct endChar from words order by endChar asc;")
    endlist = []
    result = c.fetchall()
    for kana in result:
        kana = kana[0]
        end_chars = get_end_alias_chars(kana, mode)
        cnt = len(end_chars)
        if (cnt != 0):
            is_add = False
            for ec in end_chars:
                for s in endlist:
                    if ec in s[0]:
                        s[0].update(end_chars)
                        is_add = True
                        s[1].add(kana)
                        break
                if(is_add): break
            if(not is_add):
                endlist.append((set(end_chars), set((kana,))))

    l = len(endlist)
    print(f"size: {l} * {l}")
    cm = np.zeros((l,l), dtype=int)
    results = []
    p = Pool(8)
    for j in range(l):
        for k in range(l):
            r = p.apply_async(func=get_count, args=[[dbpath, endlist[j], endlist[k], j, k]])
            results.append(r)
    for r in results:
        r = r.get()
        cm[r[1]][r[2]] = r[0]
    
    print("")

    np.save("cm.npy",cm)
    pickle.dump(
        endlist,
        open("endList.pickle","wb")
    )
    print("")

def get_count(ls):
    dbpath = ls[0]
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    end_char_first = ls[1]
    end_char_end = ls[2]
    j, k = ls[3] , ls[4]
    cnt = 0
    for f in end_char_first[0]:
        for e in end_char_end[1]:
            c.execute("select count(distinct kana) from words where substr(firstChar,1,1)=? and endChar=?", (f,e))
            r = int(c.fetchall()[0][0])
            cnt += r
    print(f"({j},{k}) = {cnt}")
    return cnt , j , k

    

def get_end_alias_chars(kana, mode):
    if(mode == 0): return (kana,)
    if(len(kana) > 1):
        # 長音あるいは小文字付き
        if(kana[-1] == "ー"):
            if(mode % 17 == 0):
                # 長音無視
                return get_end_alias_chars(kana[:-1], mode)
            elif (mode % 19 == 0):
                # 母音取り
                charset =  "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
                charset += "ハヒフヘホマミムメモヤ　ユ　ヨラリルレロワヰ　ヱヲ"
                charset += "ガギグゲゴザジズゼゾダジヅデドバビブベボパピプペポ"
                charset += "ァィゥェォヵ　　ヶ　ャ　ュ　ョヮ　ッ　　　　　　　"
                if(kana[-2] in charset and kana[-2] != "　"):
                    pos = (charset.find(kana[-2]) + 1) % 5 - 1
                    mother = "アイウエオ"
                    return get_end_alias_chars(mother[pos], mode)
                elif (kana[-2] == "ン"):
                    return get_end_alias_chars(kana[-2], mode)
                else:
                    return get_end_alias_chars(kana[:-1], mode)
            elif (mode % 23 == 0):
                # 長音負け
                return ()
        elif (kana[-1] in "ァィゥェォヵヶャュョッヮ"):
            if(mode % 5 == 0):
                # 小文字を変換
                charset = "アイウエオカケヤユヨツワ"
                return get_end_alias_chars(charset["ァィゥェォヵヶャュョッヮ".find(kana[-1])], mode)
            elif (mode % 7 == 0):
                # 小文字を除く
                return get_end_alias_chars(kana[:-1], mode)
            elif (mode % 11 == 0):
                # 小文字は負け
                return ()
        return _trans((kana,),mode)
    elif (kana[0] == "ン" and mode % 31 != 0):
        return () 
    else:
        rtn = [kana,]
        return _trans(rtn,mode)

def _trans(rtn, mode, cnt=0):
    rtn = set(rtn)
    if(mode == 0): return tuple(rtn)
    # ジ<=>ヂ変換則
    if (mode % 37 == 0):
        for r in copy.deepcopy(rtn):
            if ("ジ" == r[0]):
                rtn.add(r.replace("ジ","ヂ"))
            elif ("ヂ" == r[0]):
                rtn.add(r.replace("ヂ","ジ"))
    # ズ<=>ヅ変換則
    if (mode % 41 == 0):
        for r in copy.deepcopy(rtn):
            if ("ズ" == r[0]):
                rtn.add(r.replace("ズ","ヅ"))
            elif ("ヅ" == r[0]):
                rtn.add(r.replace("ヅ","ズ"))
    # ヲ<=>オ変換則
    if (mode % 43 == 0):
        for r in copy.deepcopy(rtn):
            if ("ヲ" == r[0]):
                rtn.add(r.replace("ヲ","オ"))
            elif ("オ" == r[0]):
                rtn.add(r.replace("オ","ヲ"))
    if(mode % 2 == 0):
        # 濁点変換則
        charset =  "カキクケコサシスセソタチツテトハヒフヘホウ"
        charset += "ガギグゲゴザジズゼゾダヂヅデドバビブベボヴ"
        for r in copy.deepcopy(rtn):
            index = charset.find(r[0])
            if (index == -1): continue
            if (index < 21) : index += 21
            else: index -= 21
            rtn.add(charset[index] + r[1:])
    if(mode % 3 == 0):
        # 半濁点変換則
        charset = "ハヒフヘホパピプペポ"
        for r in copy.deepcopy(rtn):
            index = charset.find(r[0])
            if (index == -1): continue
            if(index < 5) : index+=5
            else: index-=5
            rtn.add(charset[index] + r[1:])
    if(cnt == len(rtn)):
        return tuple(rtn)
    else:
        return _trans(rtn, mode, len(rtn))
        

if __name__=="__main__":
   main(sys.argv[1], int(sys.argv[2]))