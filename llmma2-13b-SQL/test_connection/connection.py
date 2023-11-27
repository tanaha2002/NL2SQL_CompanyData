import logging
import sys
import psycopg2
import streamlit as st
import os
from sqlalchemy import create_engine,text
# Thêm đường dẫn của thư mục chứa file hiện tại vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(parent_dir)

from llama_index import SQLDatabase
logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
url = 'postgresql://postgres:admin123@18.143.92.192:5432/Odoo_sql'

engine = create_engine(url)
postgre = engine.connect()


table_defines = ['crm_lead','crm_lost_reason','crm_recurring_plan','crm_stage','mail_activity','res_partner']
sql_database = SQLDatabase(engine=engine, include_tables=table_defines,sample_rows_in_table_info=3)


print(sql_database.get_table_columns)