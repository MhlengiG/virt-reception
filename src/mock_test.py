import requests
import time

# MCU 1: Send request
print("📤 Sending user_input: 'Where is the control lab?'")
send_res = requests.post("http://localhost:5000/chat", json={"user_input": "Where is the control lab?"})
print("🔁 Chat response:", send_res.json())

# MCU 2: Poll for response
print("\n📥 MCU 2 requesting the chatbot response...")
time.sleep(1)
res = requests.get("http://localhost:5000/get-response")
print("📩 Chatbot response received:", res.json())

# MCU 2: Acknowledge receipt
print("\n✅ MCU 2 confirming receipt of response...")
ack_res = requests.post("http://localhost:5000/confirm-receipt", json={"ack": True})
print("📬 Acknowledgment status:", ack_res.json())

# MCU 2: Check again to confirm cleared
print("\n🔁 MCU 2 tries to get response again (should be cleared)...")
time.sleep(1)
res = requests.get("http://localhost:5000/get-response")
print("📩 Chatbot response received:", res.json())
