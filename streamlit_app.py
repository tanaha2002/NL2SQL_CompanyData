import openai
import os
import time
from PIL import Image
import streamlit as st
from modules import prompt_prepare, llm, db, cache_processing, sentence_embbeding



openai.api_key = st.secrets['api_secret']
# App title
st.set_page_config(page_title="🤯🐼 Odoo CRM Chatbot")

image = Image.open("ai.png")
st.sidebar.image(image,width=280,)
with st.sidebar:
    st.title('⚡⛈️  Odoo CRM ⚡⛈️  \n')

    # st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')








if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Sup!!!, cần tìm thông tin gì trong cơ sở dữ liệu hả?"}]


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Sup!!!, cần tìm thông tin gì trong cơ sở dữ liệu hả?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
#load image to markdown


if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# submit_button = st.button(label='Submit')
table_defines = ['crm_lead','crm_lost_reason','crm_tag', 'crm_tag_rel', 'crm_stage','mail_activity','res_partner', 'res_users', 'res_company', 'utm_campaign', 'utm_medium', 'utm_source']
# Use st.cache to cache the prompt_handle object creation
@st.cache_resource
def create_prompt_handle():
    prompt_handle = prompt_prepare.PromptHandle(table_defines)
    prompt_handle.connect_to_db()
    return prompt_handle

# Create or retrieve the prompt_handle object
prompt_handle = create_prompt_handle()

        
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            #caculate cosine similarity of prompt with raw cache
                
            # response = prompt_handle.process_query(prompt, table_defines,st)
            sql,response = prompt_handle.Groupchat(prompt,st)
            st.write(sql)
            st.write(response)
            message = {"role": "assistant", "content":sql}
            message2 = {"role": "assistant", "content":response}
            st.session_state.messages.append(message)
            st.session_state.messages.append(message2)
