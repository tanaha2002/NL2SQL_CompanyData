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
# load .env file
load_dotenv()

assert os.environ.get("OPENAI_API_KEY")

# get openai api key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ------------------ helpers ------------------


# def safe_get(data, dot_chained_keys):
#     """
#     {'a': {'b': [{'c': 1}]}}
#     safe_get(data, 'a.b.0.c') -> 1
#     """
#     keys = dot_chained_keys.split(".")
#     for key in keys:
#         try:
#             if isinstance(data, list):
#                 data = data[int(key)]
#             else:
#                 data = data[key]
#         except (KeyError, TypeError, IndexError):
#             return None
#     return data


# # def response_parser(response: Dict[str, Any]):
#     return safe_get(response, "choices.0.message.content")


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

def chat_with_openai(prompt, model="gpt-3.5-turbo", max_tokens=150, temperature=0.0, delay_time=0.01):
    start = time.time()
    answer = ""
    full_response = ""
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f'{prompt}',
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )
   
    for chunk in response:
        print(answer, end="", flush=True)
        full_response += answer
        # yield full_response
        event_time = time.time() - start
        event_text = chunk.choices[0].delta
        answer = event_text.content
        
        time.sleep(delay_time)

    return full_response

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

    new_prompt = f"""{prompt} {prompt_suffix}\n\n{cap_ref}\n\n{cap_ref_content}"""

    return new_prompt
