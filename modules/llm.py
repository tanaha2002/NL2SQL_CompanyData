"""
Purpose:
    Interact with the OpenAI API.
    Provide supporting prompt engineering functions.
"""



import sys
from dotenv import load_dotenv
import os
from typing import Any, Dict
import openai
import time
import streamlit as st
# load .env file
load_dotenv()

openai.api_key = st.secrets['api_secret']

#set base to our mistral server (it's required to use version 0.28.0)
# openai.api_base = "http://171.235.90.182:1234/v1"
# openai.api_key = ""


# ------------------ content generators ------------------


def prompt(prompt: str, model: str = "gpt-3.5-turbo-0613") -> str:
    # validate the openai api key - if it's not valid, raise an error
    if not openai.api_key:
        sys.exit(
            """
ERORR: OpenAI API key not found. Please export your key to OPENAI_API_KEY
Example bash command:
    export OPENAI_API_KEY=<your openai apikey>
            """
        )

    response = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content





def chat_with_openai(prompt, st, model="gpt-3.5-turbo-1106", max_tokens=1250, temperature=0.0, delay_time=0.01, num_retries=3):
    start = time.time()
    answer = ""
    full_response = ""
    retry_count = 0
    print(prompt)
    system_message = "A Data Engineer. You follow an approved plan. Generate the initial SQL based on the requirements provided. Send it to the Sr Data Analyst to be executed."
    while retry_count <= num_retries:
        try:
            response = openai.ChatCompletion.create(
             
                model=model,
                messages=[
                    {
                        
                        "role": "user",
                        "content": prompt,
                    }
                ],
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                request_timeout=5
            )
            
            placeholder = st.empty()
            for chunk in response:
                print(answer, end="", flush=True)
                placeholder.markdown(full_response)
                full_response += answer
                event_time = time.time() - start
                event_text = chunk.choices[0].delta
                if "content" in event_text:
                    answer = event_text["content"]

            
            
            return full_response
        
        except Exception as e:
            retry_count += 1
            print(f"Retry attempt {retry_count} after API error: {e}")
            time.sleep(delay_time)
    
    return "API error, please try again later"




def set_embedding_cache(prompt, model="text-embedding-ada-002"):
    embedding = openai.Embedding.create(input=prompt, model=model)
    return embedding['data'][0]['embedding']

def add_cap_ref(
    prompt: str, prompt_suffix: str, cap_ref: str, cap_ref_content: str
) -> str:
    """
    Attaches a capitalized reference to the prompt.
    Example
        prompt = 'Refactor this code.'
        prompt_suffix = 'Make it more readable using this EXAMPLE.'
        cap_ref = 'EXAMPLE'
        cap_ref_content = 'def foo():\n    return True'
        returns 'Refactor this code. Make it more readable using this EXAMPLE.\n\nEXAMPLE\n\ndef foo():\n    return True'
    """

    new_prompt = f"""{prompt} {prompt_suffix}\n{cap_ref}\n{cap_ref_content}"""

    return new_prompt


