from dotenv import load_dotenv
import os
from modules_.db import PostgresDB
from modules import llm
import datetime
from modules.sentence_embbeding import SentenceEmbedding
from modules.cache_processing import CacheHandle
import random
import streamlit as st
# @st.cache(allow_output_mutation=True)
# def connect_to_db():
#     db = PostgresDB()
#     db.connect_with_url(st.secrets['DB_URL'])
#     return db

class PromptHandle:
    def __init__(self,table_names) -> None:
        load_dotenv()
        # os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        os.environ['DB_URL'] = st.secrets['DB_URL']
        self.db = PostgresDB()
        self.YEAR = datetime.datetime.now().year
        self.START_SQL_DELIMITER = "--- SQL Query ---"
        self.END_SQL_DELIMITER = "--- End SQL Query ---"
        self.POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
        self.RESPONSE_FORMAT = "RESPONSE_FORMAT"
        self.INTRODUCTION = ""
        self.threshold = 0.8
        
        self.connect_to_db()
        ## ----------- INIT CACHE ---------------##
        self.cache_process = CacheHandle()
        self.status = self.cache_process.response
        if self.status ==200:
            self.cache_process.connect_db()
            
            #raw cache
            self.raw_cache = self.cache_process.get_raw_cache()
            self.raw_cache_dict = self.cache_qa_format()
        else:
            print('Failed Init')
            print(self.status)
        
        self.template_da = f"""you are a data analyst. you extract the main key word to retrieve the data from the database. you use the data to create a simple report that represent the main key in question. you send the report to the data engineer to be create and executed the query. So your task is really important. Answer report follow REPORT FORMAT.

        DATA ANALYST REPORT
        1. Question (User question): {{}}
        2. Keywords 
        3. Explain user question to Data Enginner more clearly understand
        4. Tips:For instance, using ILIKE '%key%' in a query would match any records where the specified field contains the substring 'key', regardless of what comes before or after it. This flexibility makes the query more tolerant to variations or potential mistakes in syntax or spelling.
        5. Pseudo SQL Query
        END DATA ANALYST REPORT
        """
        self.response_de_head = f""""
        {{}}
        \n
        When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
        \n\nUse these TABLE_DEFINITIONS to satisfy the database SQL query as a PostgreSQL format.\n\n"""

        self.response_de_tail = f"""\nRespond in this format RESPONSE_FORMAT. I need to be able to easily parse the sql query from your response. Also THINK as a user, if your are user, what default information you want to GET?   

        RESPONSE_FORMAT


                    --- SQL Query ---
                    sql query exclusively as a raw text
                    --- End SQL Query ---

        """
        self.table_definitions = self.get_table_definitions(table_names)
        self.template_de = llm.add_cap_ref(
            self.response_de_head,
            self.table_definitions,
            self.response_de_tail,
            ""
        )
        ## -------------INIT DONE----------------##
    def connect_to_db(self):
        # self.db.connect_with_url(os.environ['DB_URL'])
        self.db.connect_with_url(st.secrets['DB_URL'])

    def get_table_definitions(self, table_names):
        return self.db.get_multiple_table_definitions_for_prompt(table_names)
    
    def get_cosine_question(self, query):
        return llm.get_cosine_question(query)

    def add_cap_ref_to_prompt(self, query, table_definitions):
        prompt = llm.add_cap_ref(
            query,
            f"\n\nUse these {self.POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
            self.POSTGRES_TABLE_DEFINITIONS_CAP_REF,
            table_definitions,
        )
        

                
                
        prompt = llm.add_cap_ref(
            prompt, 
            f"\n\nRespond in this format {self.RESPONSE_FORMAT}. I need to be able to easily parse the sql query from your response. Also THINK as a user, if your are user, what you INFORMATION you want to GET? because we have like 300+ columns then you should be able to KNOW what you want. And alway get columns name. And current year is {self.YEAR}. And make sure this query is able to instantly run.", 
            # f"\n\nRespond in this format {self.RESPONSE_FORMAT}. I need to be able to easily parse the sql query from your response. And alway get columns name. If time is not mentioned then the default is DATETIME.NOW(), make sure query is able to instantly run.", 
            self.RESPONSE_FORMAT, 
            f"""
            
            {self.START_SQL_DELIMITER}
            sql query exclusively as a raw text
            {self.END_SQL_DELIMITER}

            """
        )
        return prompt
    def normal_cap_ref(self, prompt):
        return prompt+ f"\n\n Senior Assistant of BlueBoltSoftware, You follow query of user to response as a human assistant. (You can handle query about Odoo module CRM, query and get result)"
    def chat_with_openai(self, prompt,st):
        return llm.chat_with_openai(prompt,st)

    def extract_sql_query(self, prompt_response):
        return prompt_response.split(self.START_SQL_DELIMITER)[1].split(self.END_SQL_DELIMITER)[0].strip()

    def run_sql_query(self, sql_query):
        return self.db.run_sql(sql_query)

    def parse_query(self,query,table_names,st):
        try:
            #if query contain \sql at the first, then it should go to determine sql query
            if query[0:4] == "\\sql":
                result = self.process_query(query[4:],table_names,st)
                return result
            else:
                prompt = self.normal_cap_ref(query)
                self.chat_with_openai(prompt,st)
                return None
        except Exception as e:
            #end transaction
            self.db.conn.rollback()
            print(f"Error: {e}")

    
    def add_cosine_ref(self,query,cosine_list):
        prompt = query + "\n\n Here is some example you can learn, just learn from it, you shouldn't copy it, it have a cosine similarity with your query: \n --EXAMPLE----"
        for row in cosine_list:
            prompt = llm.add_cap_ref(
                prompt,
                f"\n question: {row[0]} \n\n answer: {row[1]}",
                "",
                ""

            )
        prompt = prompt + "\n\n --END EXAMPLE----"
        return prompt




    def add_knowledged_base(self,query):
        #get random 300 question from raw cache
        
        random_knowledge_base = random.sample(self.raw_cache, 50)
        prompt = query + "\n Here is some knowledge base you can learn, just learn from it: \n --EXAMPLE----"
        for row in random_knowledge_base:
            prompt = llm.add_cap_ref(
                prompt,
                f"\n question: {row[1]} \n\n answer: {row[2]}",
                "",
                ""

            )

        prompt = prompt + "\n --END EXAMPLE----"
        return prompt

   



    def da_report(self,query,st):
        final_prompt  = self.template_da.replace("{}",query)
        print(f"------------------GET DA REPORT------------------")
        print(f'{final_prompt}')
        print(f"------------------END DA_REPORT------------------")
        da_report = self.chat_with_openai(final_prompt, st)
        return da_report


    def cache_qa_format(self):
        raw_cache_dict = []
        for item in self.raw_cache:
            raw_cache_dict.append({"Question":item[1],"Answer":item[2]})
        return raw_cache_dict

    def get_answer(self, report_da, st):

        result = ""
        query = f"\n\nUsing report of DATA ANALYST REPORT to get insight of question. You are a Data Engineer. Generate the SQL that match with TABLE_DEFINITIONS can be executed.\n\n{report_da}"
        template_de = self.template_de.replace("{}",query)
        print(f"\n------------------GET ANSWER------------------")
        print(f'{template_de}')
        print(f"------------------END GET ANSWER------------------")
        sql_ = ""
        sql_query = ""
        description = ""
        try:
            full_repsonse = self.chat_with_openai(template_de, st)
            #split sql
            sql_query = self.extract_sql_query(full_repsonse)
            sql_ = sql_query
            
            result,description = self.run_sql_query(sql_)
            print(f"---------------result in get answer-----------------")
            print(result)
            print(f"---------------end result in get answer-----------------")
        except Exception as e:
            result = f"Failed to execute the query. Error: {e}"
            print(f"---------------result in exception get answer-----------------")
            print(result)
            print(f"---------------end result in exception get answer-----------------")
        return sql_query,result,description
    

    def Groupchat(self,query,st):
        #sample raw cache
        sample_cache = random.sample(self.raw_cache_dict, 50)
        sample_prompt = f"""\nHere is some sample you can learn to get the insight and context of our database structure.\n ---------EXAMPLE---------\n"""
        for item in sample_cache:
            sample_prompt += f"Q: {item['Question']}\nA: {item['Answer']}\n"
        sample_prompt += f"---------END EXAMPLE---------\n"
        query = f"{query}\n{sample_prompt}"
        report_da = self.da_report(query,st)
        sql,result,description = self.get_answer(report_da,st)
        max_try = 3
        print(f"\n\n------------------RESULT------------------\n{result}\n------------------END RESULT------------------\n")
        while 'Failed' in result and max_try > 0:
            #rollback the curr
            self.db.conn.rollback()
            print(f"\nFailed {max_try} times\n")
            #give prompt to user to edit the query
            new_prompt = f"""\nYou generate the wrong syntax SQL query, please notice that. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. Focus on YOUR PREVIOUS SQL WRONG to correct it.\n\n---------YOUR PREVIOUS SQL WRONG---------\n
            {sql}
            \n---------END PREVIOUS SQL WRONG---------\n
            \n---------YOUR ERROR---------\n
            {result}
            \n---------END ERROR---------\n
            \n---------USER QUESTION---------\n
            {query}
            \n---------END USER QUESTION---------\n
            \n\n
            """
            sql,result,description = self.get_answer(new_prompt,st)
            max_try -= 1
        #get column name of curr
        return sql,result,description
    




    def process_query(self, query, table_names,st):
        
        table_definitions = self.get_table_definitions(table_names)

        ## --------------- PROMPT  + COSINE CACHE ----------------##
        # cosine_threshold_pass = []
        #caculate cosine similarity
        # cosine_question = self.cache_process.get_cosine_question(query) 
        # print(cosine_question)
        # for row in cosine_question:
            # if row[1] > self.threshold:
            #     answer = self.cache_process.search_raw_cache(row[0])[1]
            #     print("question:",row)
            #     print("answer:",answer)
            #     #get list of question that pass threshold
            #     cosine_threshold_pass.append((row[0],answer))

        #add additonal prompt cosine question
        # if len(cosine_threshold_pass) > 0:
            
            # prompt = self.add_cosine_ref(query,cosine_threshold_pass)
        # prompt = query

        # prompt = self.add_cap_ref_to_prompt(prompt, table_definitions)
        #define just like normal, without cosine question
        # else:
        prompt = self.add_cap_ref_to_prompt(query, table_definitions)
        prompt = self.add_knowledged_base(prompt)
        print("------------------------PROMPT-------------------------")

        #remove duplicate space
        # prompt = " ".join(prompt.split())

        print(prompt)
        prompt_response = self.chat_with_openai(prompt,st)
        sql_query = self.extract_sql_query(prompt_response)
       
        result,description = self.run_sql_query(sql_query)
       

        return result
    
    
