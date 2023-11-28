import requests
import streamlit as st
from pydantic import BaseModel
import torch
import numpy as np
table_defines = [
    'crm_lead', 'crm_lost_reason', 'crm_tag', 'crm_tag_rel', 'crm_stage',
    'mail_activity', 'res_partner', 'res_users', 'res_company', 'utm_campaign',
    'utm_medium', 'utm_source'
]

url_onnx = "http://18.143.174.234:4001"


def send_request():
    init = requests.post(url_onnx + '/init')
    response = requests.post(url_onnx + '/result',params={'text': 'Bạn là gà hay thóc?'})
    
    if response.status_code == 200:
        print("Request successful!")
        tensor = np.array(response.json()['embedding'])
        print(tensor)
    else:
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.json())

send_request()
