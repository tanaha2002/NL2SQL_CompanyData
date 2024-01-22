import openai
import os
import time
from PIL import Image
import streamlit as st
from modules import prompt_prepare, llm, db, cache_processing, sentence_embbeding
import json
import requests
import pandas as pd
openai.api_key = st.secrets['api_secret']
# App title
st.set_page_config(page_title="🤯🐼 Database @$J#L!%H:")

image = Image.open("ai.png")


with st.sidebar:
    st.title('⚡⛈️  Odoo CRM ⚡⛈️  \n')
    st.subheader('Đôi lời bộc bạch')
    st.markdown('<justify>🤦‍♂️Bot hiện đang trong giai đoạn thử nghiệm, mọi câu trả lời có thể sẽ không được tốt, sẽ cố gắng cải thiện trong tương lai. Mong bạn thông cảm... 🫂</justify>', unsafe_allow_html=True)
    st.subheader('Trạng thái')
    st.success('Đã có API key', icon='✅')
    st.subheader('Mô hình')
    #dropdown
    selected_model = st.sidebar.selectbox('Chọn mô hình', ['gpt-3.5-turbo-0613'], key='selected_model')
    st.sidebar.image(image, width=220)
    









if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Sup!!!, cần tìm thông tin gì trong cơ sở dữ liệu hả?"}]


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.write(message["content"])
        if "result" in message:
            st.table(message["result"])
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
url_onnx = st.secrets['url_onnx']
@st.cache_resource
def create_prompt_handle():
    prompt_handle = prompt_prepare.PromptHandle(table_defines)
    prompt_handle.connect_to_db()
    return prompt_handle


# Create or retrieve the prompt_handle object
# prompt_handle = create_prompt_handle()
init_val = create_prompt_handle()

if init_val.status == 200:    
    if st.session_state.messages[-1]["role"] != "assistant":
        
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    #caculate cosine similarity of prompt with raw cache
                        
                    # response = prompt_handle.process_query(prompt, table_defines,st)
                    sql,response,description = init_val.Groupchat(prompt,st)
                    print(f"sql: {sql}")
                    print(f"response: {response}")
                    print(f"description: {description}")
                    if sql == None or description == None:
                        st.session_state.messages.append({"role": "assistant", "content":response})
                    else:
                        if 'Failed' in response:
                            st.error('Failed to attemp to API 3 times, may you need re-check your billing or API ❌')
                            
                        else:
                            st.write(sql)
                            #add description (column name)  to response
                            print(description)
                            columns = [col[0] for col in description]
                            print(response)
                            merge_response = []
                            for row in response:
                                merge_response.append(dict(zip(columns, row)))
                            st.write("Results:")
                            st.table(merge_response)
                            df = pd.DataFrame(merge_response)
                            table_html = df.to_html(index=False, justify='center', classes=['dataframe'])
                            
                            # for idx, row in enumerate(response):
                            #     st.write(f"{idx} - Name: {row[0]}, Value: {row[1]}")
                            message = {"role": "assistant", "content":sql}
                            message2 = {"role": "assistant", "result":merge_response}
                            st.session_state.messages.append(message)
                            st.session_state.messages.append(message2)
else:
    st.error('Failed to init api, please init first! ❌')