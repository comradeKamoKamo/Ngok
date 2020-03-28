# CPU.py
import sys
import pickle
import sqlite3
import copy

import numpy as np
from gensim.models import word2vec


import words_analyze
import parse_dic
import simulator

MODE = 21930

def cpu(wordlog, c, cm, endList, model) :
    word = wordlog[-1]
    wordend = words_analyze.get_end_alias_chars(
        parse_dic.get_edge_kana(word[1])[1]
        , MODE)
    if len(wordend) == 0 :
        return None, False
    end_index = -1
    for i, e in enumerate(endList):
        if set(wordend).issubset(e[0]):
            end_index = i
            break
    r = simulator.attack_st(cm, end_index)
    if r == -1:
        return None, True
    end_chars = endList[r][1]
    first_chars = endList[end_index][0]

    wordlist = []
    for fc in first_chars:
        for ec in end_chars:
            c.execute("select surface,kana from words where substr(firstChar,1,1)=? and endChar=? group by kana;", (fc, ec))
            wordlist.extend(c.fetchall())

    # 言われた単語はダメ
    kana_list = [v[1] for v in wordlog]
    for w in copy.deepcopy(wordlist):
        if w[1] in kana_list:
            wordlist.remove(w)
    
    # 言う言葉がなくなる
    if not wordlist:
        cm[end_index][r] = 0
        return cpu(wordlog, c, cm, endList, model)

    try:
        word_vec = model.wv[word[0]]
        # 言われた言葉に似ている言葉を探す
        sim = 0
        r_word = wordlist[0]
        for wr in wordlist:
            try:
                s = model.wv.similarity(word_vec, model.wv[wr[0]])
                if s > sim :
                    sim = s
                    r_word = wr
            except:
                pass
        wordlog.append(r_word)
    except:
        # 言われた言葉がword2vec未定義なら、
        # 候補の中で一番短い言葉を返す
        wordlog.append(
            sorted(wordlist, key=len)[0]
        )


    return wordlog, cm

def data_load():
    cm = np.load("output_21930/cm_clean.npy")
    endList = pickle.load(open("output_21930/endList_clean.pickle", "rb"))
    con = sqlite3.connect("data/wordset.db")
    c = con.cursor()
    model = word2vec.Word2Vec.load("data/word2vec/jawiki.model")
    return cm, endList, con, c, model


if __name__=="__main__" :
    cm, endList, con, c, model = data_load()

    wordlog = [("しりとり","シリトリ")]
    print("しりとり/シリトリ")
    while True:
        print("あなたの単語", end=":")
        surface = input()
        print("そのヨミガナ", end=":")
        kana = input()
        wordlog.append((surface,kana))
        wl, cm = cpu(wordlog, c, cm, endList, model)
        if wl is None:
            if cm:
                # ユーザの勝ち
                print("CPUは言葉が思いつきません。あなたの勝ちです。")
            else:
                print("あなたの負けです")
            break
        else:
            print(f"CPU: {wordlog[-1][0]} / {wordlog[-1][1]}")
