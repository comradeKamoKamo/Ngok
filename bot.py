# Twitter Bot Program

import os
import time
import re
import copy
import logging
import requests
import pickle
import xml.etree.ElementTree as ET

import tweepy
import jaconv

import cpu

def main():

    cm, endList, con, c, con_kv, c_kv = cpu.data_load()

    api = get_api()
    players = []
    try:
        old_players = pickle.load(open("players.pickle","rb"))
        players = old_players
    except Exception:
        pass
    last_save_time = time.time()
    while True:
        try:
            replies = api.mentions_timeline(count=1, tweet_mode="extended")
        except tweepy.TweepError as e:
            logging.error(f"TweepError({e.api_code}): {e.reason}")
            time.sleep(30)
            continue
        for reply in replies:
            text = get_display_text(reply)
            if reply.author.screen_name == "_ngok_": continue # 自己ループを避ける
            
            # ユーザーデータ取得
            now_player = [p for p in players if p.user_id == reply.author.id]
            if not now_player :
                # 未知のアカウント
                now_player = [player(reply.author.id, reply.author.screen_name, cm)]
                players.append(now_player[0])
            now_player = now_player[0]

            # リプライが最新のものでなければ無視
            if reply.id == now_player.status_id:
                continue
            else:
                now_player.status_id = reply.id
                logging.info(f"@{reply.author.screen_name} (id: {reply.id}) : {text}")
            
            # 「しりとり」が含まれていたらリセットする
            if "しりとり" in text:
                now_player.wordlog = [("しりとり","シリトリ")]
                wl, cm = cpu.cpu(now_player.wordlog, c, now_player.cm, endList, c_kv)
                if winning(api, wl, cm, now_player, players): continue
                reply_to_status(api, 
                                f"@{reply.author.screen_name} {get_word(wl[-1])}",
                                now_player.status_id
                                )
            # 未知のユーザーで「しりとり」以外は無視
            elif not now_player.wordlog:
                continue
            else:
                # textを解釈する
                # surfaceとkanaを分離　りんご（リンゴ）
                surface , kana = "" , ""
                # 曖昧モードのフラグ
                aimai_flag = False
                if "（" in text and "）" in text:
                    # 指定あり
                    surface, kana = text.split("（")[0] , text.split("（")[-1][0:-1]
                    if not surface or not kana:
                        reply_to_status(api, 
                                    f"@{reply.author.screen_name} 「{text}」は形式が不正です。"
                                    + f"単語（タンゴ）の形で明示してください。",
                                    now_player.status_id
                                )
                        continue
                    elif not is_kataonly(kana):
                        reply_to_status(api, 
                                    f"@{reply.author.screen_name} 「{kana}」はカタカナのみで構成されていません。",
                                    now_player.status_id
                                )
                        continue
                else:
                    # 指定なし
                    # 改行を消す
                    text = text.replace("\n","")
                    # DBに問い合わせる
                    c.execute("select kana from words where surface=?", [text])
                    try:
                        result = c.fetchall()[0][0]
                    except IndexError:
                        result = None
                    # それでもダメ
                    if result is None:
                        kt = jaconv.hira2kata(text)
                        if is_kataonly(kt):
                            # カタカナのみに変換できた！
                            result = kt
                        else:
                            # Yahooの力を借りる
                            try:
                                yk = get_kana_from_yahoo(text)
                            except Exception as e:
                                logging.error(f"Yahoo failed.")
                                yk = None
                            if yk is None:
                                # 完全に読み取得できず。
                                reply_to_status(api, 
                                    f"@{reply.author.screen_name} 「{text}」の読みが推定できませんせした。"
                                    + f"単語（タンゴ）の形で明示的に指定できます。",
                                    now_player.status_id
                                )
                                continue
                            elif not is_kataonly(jaconv.hira2kata(yk)):
                                # 読みが取得できるも正確でない可能性が高い
                                aimai_flag = True
                            result = jaconv.hira2kata(yk)
                    surface, kana = text, result
                # CPUに渡す
                now_player.wordlog.append( (surface, kana) )
                wl, cm = cpu.cpu(now_player.wordlog, c, now_player.cm, endList, c_kv)
                if winning(api, wl, cm, now_player, players): continue
                tweet = f"@{reply.author.screen_name} {get_word(wl[-1])}"
                if aimai_flag:
                    tweet += "　※読みが正常に推定できませんでした。単語（タンゴ）の形で明示的に指定できます。"
                reply_to_status(api, tweet, now_player.status_id)                
        time.sleep(13)      
        if time.time() - last_save_time > 60*60:
            # 1時間経過したら保存
            pickle.dump(players, open("players.pickle","wb"))
            last_save_time = time.time()

def get_kana_from_yahoo(text):
    client_id = os.environ.get("YAHOO_ID")
    target_url = "https://jlp.yahooapis.jp/FuriganaService/V1/furigana"
    data = {
        "appid": client_id,
        "grade": "1",
        "sentence": text
    }
    response = requests.post(target_url, data=data)

    result_set = ET.fromstring(response.text)
    if result_set.tag == "Error":
        try:
            reason = result_set.get_children()[0].text
        except Exception:
            reason = "Unknown"
        logging.error(f"Yahoo Error : {reason}")
        return None
    word_list = result_set.getchildren()[0].getchildren()[0]

    kana = ""
    for word in word_list:
        try:
            kana += [w for w in word.getchildren() if w.tag.endswith("Furigana")][0].text
        except IndexError:
            kana += [w for w in word.getchildren() if w.tag.endswith("Surface")][0].text
    return kana



def get_word(word):
    return word[0] + "（" + word[1] + "）"

def is_kataonly(text):
    return re.compile(r"([\u30A1-\u30F4]|[ー])+").fullmatch(text)

def reply_to_status(api, text, status_id):
    while True:
        try:
            api.update_status(text, in_reply_to_status_id=status_id)
            logging.info(f"Replied {status_id} : {text}")
            break
        except tweepy.TweepError as e:
            logging.error(f"TweepError({e.api_code}): {e.reason}")
            if e.api_code == 187:
                # 重複は無視
                break
            if e.api_code == 185:
                # 制限
                time.sleep(15*60) # 15分停止
                continue
            # それ以外も無視nano
            break
           
def winning(api, wl, cm, now_player, players):
    if wl is None:
        if cm:
            # ユーザーの勝ち
            reply_to_status(api, f"@{now_player.screen_name} ンゴック君は何も思いつきません。あなたの勝ちです。", now_player.status_id)
        else:
            # ユーザーの負け
            reply_to_status(api, f"@{now_player.screen_name}「ン」で終わったのであなたの負けです。", now_player.status_id)
        [players.remove(p) for p in players if p.user_id == now_player.user_id]
    return wl is None

def get_display_text(tweet):
    s , e = tuple(tweet.display_text_range)
    return tweet.full_text[s:e]

def get_api():
    #OAuth
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    auth = tweepy.OAuthHandler(api_key,api_secret)
    auth.set_access_token(access_token,access_token_secret)
    api = tweepy.API(auth)
    return api

class player:
    def __init__(self, user_id, sc, cm):
        self.user_id = user_id
        self.status_id = None
        self.screen_name = sc
        self.wordlog = []
        self.cm = copy.deepcopy(cm)
        self.lasttime = time.time()

if __name__=="__main__":
    fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)
    main()