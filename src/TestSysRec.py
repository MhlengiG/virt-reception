import requests

API_URL = "http://3.78.230.164:5000/get-response"  # Your EC2 IP

def get_response():
    try:
        res = requests.get(API_URL)
        res.raise_for_status()
        data = res.json()
        print("Response status:", data.get("status"))
        print("Response:", data.get("response"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    get_response()
