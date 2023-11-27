import sqlite3

RAW_CACHE = 'text2SQL.db'
def get_raw_cache():
        conn = sqlite3.connect(RAW_CACHE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM cache")
        raw_cache = cur.fetchall()
        conn.close()
        return raw_cache

data = get_raw_cache()
print(data)