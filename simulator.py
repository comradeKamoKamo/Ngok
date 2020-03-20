# simulator.py しりとり数値シミュレーション
import numpy as np
import copy
from multiprocessing import Pool

PROCESSES = 8

def simulate(cm, funcA, funcB):
    winner = -1
    acnt = 0
    bcnt = 0
    r = -6  # リ
    log = []
    while True :
        r = funcA(cm, r, log)
        if r < 0 :
            # print("B is the winner.")
            winner = 1
            break
        log.append(r)
        acnt += 1
        r = funcB(cm, r, log)
        if r < 0 :
            # print("A is the winner.")
            winner = 0
            break
        log.append(r)
        bcnt += 1
    # print(f"A count: {acnt} B count: {bcnt}")
    print(f"total count: {acnt+bcnt}")
    return winner, acnt, bcnt

# cm カラーマップデータ r 次の頭文字インデックス
# ランダム戦術
def random_st(cm, r, *args):
    # 返せる単語の総数を調べる
    wc = cm[r].sum()
    if wc == 0: return -1
    # 無作為に単語を選ぶ
    if wc == 1:
        index = 0
    else:
        index = np.random.randint(0,wc - 1)
    for i, v in enumerate(cm[r]):
        index -= v
        if  index <= 0  :
            cm[r][i] -= 1
            return i
    return -1

# 超攻撃的戦術
def attack_st(cm, r, *args):
    # rateを得る
    first_sums = cm.sum(axis=1)
    end_sums = cm.sum(axis=0)
    rates = end_sums / first_sums

    sort_index = np.argsort(rates)

    for i in reversed(sort_index):
        if cm[r][i] != 0 :
            cm[r][i] -= 1
            return i

    return -1

# 超防御的戦術
def defence_st(cm, r, *args):
    # 攻撃された文字が始端に少ないリストを作る
    index_sort = np.argsort(cm[r])
    for i in index_sort:
        if(cm[r][i] != 0):
            cm[r][i] -= 1
            return i
    return -1

# 攻撃防御可変戦術
def mild_st(cm, r, log, *args):
    # 攻撃された文字が過去にどのぐらい使われたかで攻撃か防御を決める
    if log.count(r) != 0 :
        rate = log.count(r) / len(log)
        rand = np.random.rand()
        if rand < rate:
            return defence_st(cm, r)
     
    return attack_st(cm,r)

if __name__== "__main__" :
    cm_origin = np.load("output_21930/cm_clean.npy")
    awc, bwc = 0, 0
    p = Pool(PROCESSES)
    results = []
    for i in range(8):
        cm = copy.deepcopy(cm_origin)
        r = p.apply_async(func=simulate, args=[cm, attack_st,attack_st])
        results.append(r)
    for r in results:
        r = r.get()
        if r[0] == 0 :
            awc += 1
        else:
            bwc += 1
    print(f"{awc},{bwc}")

