import requests
import time

BASE_URL = "http://3.78.230.164:5000"


def send_user_input(user_input):
    res = requests.post(f"{BASE_URL}/chat", json={"user_input": user_input})
    res.raise_for_status()
    return res.json()


def get_bot_response():
    for _ in range(10):
        res = requests.get(f"{BASE_URL}/get-response")
        res.raise_for_status()
        data = res.json()
        if data.get("status") == "ready":
            return data["response"]
        print("Waiting for response...")
        time.sleep(1)
    raise TimeoutError("Bot response not ready in time.")


def confirm_receipt():
    res = requests.post(f"{BASE_URL}/confirm-receipt", json={"ack": True})
    res.raise_for_status()
    return res.json()


if __name__ == "__main__":
    user_input = input("You: ")

    try:
        ack = send_user_input(user_input)
        print("Server ACK:", ack)

        bot_response = get_bot_response()
        print("Response Generator:", bot_response)

        receipt = confirm_receipt()
        print("Receipt Confirmed:", receipt)

    except Exception as e:
        print("Pipeline error:", e)
