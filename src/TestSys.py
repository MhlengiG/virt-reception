import requests


API_URL = "http://3.78.230.164:5000/chat"

def send_message(message):
    try:
        res = requests.post(API_URL, json={"user_input": message})
        res.raise_for_status()
        print("Response Generator:\n", res.json())
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    print("SUBSYSTEM 1 POST request simulation\n")
    while True:
        msg = input("You: ")
        if msg.lower() in ["exit", "quit"]:
            break
        send_message(msg)



