import requests

url = "http://3.78.230.164:5000/update_availability"

payload = {
    "staff_name": "Xu",
    "available_today": 1
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())

