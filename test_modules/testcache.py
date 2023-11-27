import sys
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
# Thêm đường dẫn của thư mục chứa file hiện tại vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

# Import từ file ở bên ngoài
from cache_processing import CacheHandle
from modules import prompt_prepare

cache = CacheHandle()
cache.connect_db()

# # import datetime
# # import numpy as np

# # embedding_list = [1,3,2]
# # embedding_array = np.array(embedding_list) 
# # embedding_str = str(embedding_array.tolist())

# # cache.insert("test", datetime.datetime.now(), "test", embedding_str)
# # cache.load_raw_cache()
query = "Cho tôi thông tin liên hệ khách hàng của cơ hội 'PHÒNG LAB ODOO'?"
a = cache.get_cosine_question(query)
#threshold = 0.8
# for row in a:
#     if row[1] > 0.8:
#         answer = cache.search_raw_cache(row[0])[1]
#         print(row[0])
#         print(answer)

answer = cache.search_raw_cache(query)[1]
# import sqlite3
# conn = sqlite3.connect('text2SQL.db')
# c = conn.cursor()
# c.execute("SELECT * FROM cache WHERE question = ?", (query,))
# answer = c.fetchall()
print(answer)

