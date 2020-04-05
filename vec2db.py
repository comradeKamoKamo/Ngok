import sqlite3
import logging
import time

WORD2VEC_TEXT = "data/word2vec/jawiki_normalized.kv.txt"
DB_PATH = "data/word2vec/jawiki_normalized.kv.db"

def return_column_names(n):
    if n >= 0:
        r = "keyword TEXT PRIMARY KEY,"
        for i in range(n):
            r += f" vec{i} integer,"
    else:
        r = "?,"
        for i in range(-1*n):
            r += "?,"
    return r[0:-1]

if __name__=="__main__":

    start = time.time()

    fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)

    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    with open(WORD2VEC_TEXT, "r") as f:
        fl = f.readline()
        logging.info("Start: " + fl)
        count = int(fl.split(" ")[0])
        size = int(fl.split(" ")[1])
        c.execute(f"create table kv( {return_column_names(size)} );")
        for i in range(2, count+2):
            line = f.readline()
            row = line.split(" ")
            if len(row) != 201:
                logging.warn(f"Index error: line: {i} text: {line}")
                continue
            c.execute(f"insert into kv values ({return_column_names(-1*size)});", row)
            if i % 10**4 == 0:
                logging.info(f"{i} / {count} done. {i/count*100} percent.")
                con.commit()
    logging.info("DONE!!!")
    con.commit()
    con.close()
