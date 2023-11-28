import openai
import os
import sqlite3
import psycopg2
from psycopg2.extensions import AsIs
from modules import *
import numpy as np
import datetime
# from modules.sentence_embbeding import SentenceEmbedding
from modules.sentence_embbeding import SentenceEmbedding
from dotenv import load_dotenv
import streamlit as st
import requests
RAW_CACHE = 'text2SQL.db'
import requests

class CacheHandle:
    def __init__(self) -> None:
        # self.connection_params = {
        # 'host': os.getenv("CACHE_HOST"),
        # 'user': os.getenv("CACHE_USER"),
        # 'password': os.getenv("CACHE_PASSWORD"),
        # 'database': os.getenv("CACHE_DB")
        # }
        self.connection_params = {
            'host': st.secrets['CACHE_HOST'],
            'user': st.secrets['CACHE_USER'],
            'password': st.secrets['CACHE_PASSWORD'],
            'database': st.secrets['CACHE_DB']

        }
        #--------local test-----------------
        #check if file embeddings.onnx is there
        # if not os.path.exists("./modules/embeddings.onnx"):
        #     print("embeddings.onnx not found, downloading....")

        # else:
        #     self.sentence_embedding = SentenceEmbedding("./tokenizer",
        #                                              "./modules/embeddings.onnx")
        #check the request to get embeddings.onnx
        #--------- using api ---------------
        self.url_onnx = st.secrets['url_onnx']
        self.response = None
        try:
            if requests.get(self.url_onnx).status_code == 200:
                print("embeddings.onnx is ready to use!")
                self.response = requests.post(url=self.url_onnx + 'init/').status_code
                if self.response == 200:
                    print("Init sentence embedding success!")
                    
                else:
                    print("Init sentence embedding failed!")
            else:
                self.response
                print("embeddings.onnx not found, may API error!")
        except Exception as e:
            print(f"ERROR: {e}")
        
            
        
        self.connection = None
        self.cursor = None

    #connect to db
    def connect_db(self):
        try:
            # Set autocommit mode to True to handle database creation
            self.connection = psycopg2.connect(**self.connection_params)
            
            self.connection.autocommit = True
            print("Connect db success!")
            self.cursor = self.connection.cursor()
            self.load_raw_cache()


                
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            print("Create db....")
            self.create_db()
            return False
    def create_db(self):
        try:
            # self.connection_params['database'] = os.getenv("DB_ROOT")
            self.connection_params['database'] = st.secrets['DB_ROOT']
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            # new_database_name = os.getenv("CACHE_DB")
            new_database_name = st.secrets['CACHE_DB']
            #create new database
            self.cursor.execute(f"CREATE DATABASE {new_database_name}")
            #connect to new database
            self.connection.close()
            self.connection_params['database'] = new_database_name
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            #create extension pg_vector
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            #create table
            self.create_table()

            print(f"Database {new_database_name} created successfully.")
            self.load_raw_cache()
            print(f"Success embedding raw cache and add to db!")
        except Exception as e:
            print(f"Error: {e}")
            return False
    #create table cache_vector
    def create_table(self):
        try:
            self.cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS cache_vector(
                    id BIGSERIAL PRIMARY KEY,
                    origin_question varchar(8192),
                    timestamp DATETIME,
                    type_question varchar(100)
                    embedding VECTOR(768)
                );
                '''
            )
        except Exception as e:
            print(f"Error: {e}")
            return False

        return True
    #add new data embedding to cache
    def insert(self, question, timestamp, type_question, embedding):
        try:
            embedding_str = str(embedding.tolist())
            sql  = f"INSERT INTO public.cache_vector (origin_question, timestamp, type_question, embedding) VALUES (%s, %s, %s, %s);"
            self.cursor.execute(
                sql,
                (question, timestamp, type_question, embedding_str))
            self.connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        return True
    
    def text_embedding(self, text):
        if self.response.status_code == 200:
            embedding = requests.post(url=self.url_onnx + 'result', params={'text': text})['embedding']
            embedding_ = np.array(embedding)
        # return self.sentence_embedding.embed(text)
            return embedding_
        else:
            print("Ur init current failed, please check again!")
            return False
    def search_question(self, question):
        sql = f"SELECT * FROM public.cache_vector WHERE origin_question = %s;"
        self.cursor.execute(sql, (question,))
        return self.cursor.fetchall()
    #add raw cache embedding to vector database
    def load_raw_cache(self):
        try:
            new_cache_checking = False
            raw_cache = self.get_raw_cache()
            # print(raw_cache)
            # return raw_cache
            for row in raw_cache:
                # print("Row: ", self.search_question(row[1]))
                if row[3] == 1 and self.search_question(row[1]) == []:
                    embedding = self.text_embedding(row[1])
                    self.insert(row[1], datetime.datetime.now(), "CRM", embedding)
                    new_cache_checking = True
            print(new_cache_checking)
            if new_cache_checking:
                print("Sucess load new cache from raw cache")
            else:
                print("No new cache in raw cache")
        except Exception as e:
            print(f"Error: {e}")
            return False
        return True
    
    #add new question from user that not in cache to vector database and raw cache
    def add_question_to_vector(self,question,answer,validation):
        embedding = self.text_embedding(question)
        self.insert(question, datetime.datetime.now(), "CRM", embedding)
        #add raw cache
        conn = sqlite3.connect(RAW_CACHE)
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO cache(question, answer, validation, last_time_query) VALUES(?,?,?,?)
            ''', (question, answer,validation, datetime.datetime.now())

        )
        print("Sucess save new data to raw cache")
        conn.commit()
        conn.close()

    def get_raw_cache(self):
        conn = sqlite3.connect(RAW_CACHE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM cache")
        raw_cache = cur.fetchall()
        conn.close()
        return raw_cache
    
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    def search_raw_cache(self, question):
        conn = sqlite3.connect(RAW_CACHE)
        cur = conn.cursor()
        cur.execute("SELECT question, answer FROM cache WHERE question = ?", (question,))
        question_cache = cur.fetchall()
        conn.close()
        return question_cache[0]

    def get_cosine_question(self, query):
        query_embedding = self.text_embedding(query)
        query_embedding_str = str(query_embedding.tolist())
        sql = f"SELECT * FROM cache_vector ORDER BY embedding <=> '{query_embedding_str}' LIMIT 5;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        #caculate cosine similarity for result
        score_list = []

        for row in result:
            embedding_str = row[4].strip('[]')
            embedding_array = np.array(embedding_str.split(','), dtype=float)
            cosine_score = self.cosine_similarity(query_embedding, embedding_array)
            score_list.append((row[1], cosine_score))

        return score_list
        


    
            
                
                



















# #main 
# # if __name__ == '__main__':
#     # raw_cache = load_raw_cache()
# a ="Cho tôi thông tin liên hệ khách hàng của cơ hội 'PHÒNG LAB ODOO'?"
# b ="Giai đoạn nào có doanh thu cao nhất?"
# c ="Nhân viên kinh doanh của cơ hội 'quản lý chi phí' là ai?"
# d ="Có bao nhiêu nhân viên kinh doanh? Đó là những ai?"
# e ="Phương tiện nào không thuộc bất kỳ cơ hội nào?"
# special ='Bạn là ai'
# special = llm.set_embedding_cache(special)
# special = np.array(special)
# a_a = np.array(llm.set_embedding_cache(a))
# b_b  =np.array(llm.set_embedding_cache(b))
# c_c = np.array(llm.set_embedding_cache(c))
# d_d = np.array(llm.set_embedding_cache(d))
# e_e = np.array(llm.set_embedding_cache(e))
# print((special.dot(a_a) / (np.linalg.norm(special) * np.linalg.norm(a_a))))
# print((special.dot(b_b) / (np.linalg.norm(special) * np.linalg.norm(b_b))))
# print((special.dot(c_c) / (np.linalg.norm(special) * np.linalg.norm(c_c))))
# print((special.dot(d_d) / (np.linalg.norm(special) * np.linalg.norm(d_d))))
# print((special.dot(e_e) / (np.linalg.norm(special) * np.linalg.norm(e_e))))