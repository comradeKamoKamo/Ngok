# CPU.py
import sys
import pickle
import sqlite3
import copy
import random

import numpy as np

import words_analyze
import parse_dic
import simulator

MODE = 21930

def cpu(wordlog, c, cm, endList, c_kv) :
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
        return cpu(wordlog, c, cm, endList, c_kv)

    
    try:
        word_vec = get_vec(c_kv, word[0])
        # 言われた言葉に似ている言葉を探す
        sim = 2
        r_word = wordlist[0]
        cnt = 0
        for wr in wordlist:
            try:
                s = get_similarity(word_vec, get_vec(c_kv, wr[0]))
                if s < sim :
                    sim = s
                    r_word = wr
                    cnt += 1
            except IndexError:
                pass
        if not cnt > 1:
            raise IndexError        # 良くない使い方
        wordlog.append(r_word)
    except IndexError:
        # 言われた言葉がword2vec未定義なら、
        # 候補の中で一番短い言葉を返す（+2文字まで許容）
        # ユーザービリティを考慮してちと乱数要素を入れる
        lower_list = sorted(wordlist, key=lambda w: len(w[1]))
        lowests = [w for w in lower_list if len(w[1]) - 2 <= len(lower_list[0][1])]
        random.shuffle(lowests)
        wordlog.append(lowests[0])
    return wordlog, cm

def get_vec(c_kv, surface):
    c_kv.execute("select * from kv where keyword=?;", (surface,))
    r = c_kv.fetchall()[0]
    return np.array(r[1:])

def get_similarity(vec1, vec2):
    # 正則化
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)
    # ユークリッド距離
    diff = (vec1 - vec2) ** 2
    s = diff.sum()
    return np.sqrt(s)

def data_load():
    cm = np.load("output_21930/cm_clean.npy")
    endList = pickle.load(open("output_21930/endList_clean.pickle", "rb"))
    con = sqlite3.connect("data/wordset.db")
    c = con.cursor()
    con_kv = sqlite3.connect("data/word2vec/kv.db")
    c_kv = con_kv.cursor()
    return cm, endList, con, c , con_kv, c_kv


if __name__=="__main__" :
    cm, endList, con, c, con_kv, c_kv = data_load()

    wordlog = [("しりとり","シリトリ")]
    print("しりとり/シリトリ")
    while True:
        print("あなたの単語", end=":")
        surface = input()
        print("そのヨミガナ", end=":")
        kana = input()
        wordlog.append((surface,kana))
        wl, cm = cpu(wordlog, c, cm, endList, c_kv)
        if wl is None:
            if cm:
                # ユーザの勝ち
                print("CPUは言葉が思いつきません。あなたの勝ちです。")
            else:
                print("あなたの負けです")
            break
        else:
            print(f"CPU: {wordlog[-1][0]} / {wordlog[-1][1]}")