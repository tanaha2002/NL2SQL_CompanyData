from modules.prompt_prepare import PromptHandle
from modules import llm
from modules.cache_processing import CacheHandle
import streamlit as st
import random
from modules_ import db

# prompt_handle = PromptHandle()
# prompt_handle.connect_to_db()


table_defines = ['crm_lead','crm_lost_reason','crm_tag', 'crm_tag_rel', 'crm_stage','mail_activity','res_partner', 'res_users', 'res_company', 'utm_campaign', 'utm_medium', 'utm_source']

database  = db.PostgresDB()
database.connect_with_url(st.secrets['DB_URL'])
table_definations = database.get_multiple_table_definitions_for_prompt(table_defines)
print(table_definations)
# #raw cache
# raw_cache = cache_process.get_raw_cache()
# #get random 100 rows
# random_100_rows = random.sample(raw_cache, 100)
# print(random_100_rows)