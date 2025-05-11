import requests
import pprint

API_URL = "http://3.78.230.164:5000/chat"

def send_message(message):
    try:
        res = requests.post(API_URL, json={"user_input": message})
        res.raise_for_status()
        # print("Response Generator:\n", res.json())
    except Exception as e:
        print("Error:", e)

