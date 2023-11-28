from fastapi import FastAPI
from fastapi.responses import JSONResponse
import openai
import streamlit as st
from modules import prompt_prepare, llm, db, cache_processing, sentence_embbeding
from typing import List
from fastapi import FastAPI, HTTPException


app = FastAPI()

openai.api_key = st.secrets['api_secret']

    

@app.get("/")
def check_health():
    return {"status": "OK"}


@app.post("/init/")
def init(table_defines: List[str]):
    try:
        global prompt_handle
        prompt_handle = prompt_prepare.PromptHandle(table_defines)
        prompt_handle.connect_to_db()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize prompt_handle"
        )
    return {"status": "OK"}

@app.post("/result")
def result(prompt,st):
    sql,response,description = prompt_handle.Groupchat(prompt,st)
    st.write(sql)
    return {
        "response": response,
        "sql": sql,
        "description": description
    }
    
