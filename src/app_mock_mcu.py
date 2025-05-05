from flask import Flask, request, jsonify
from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery
from ChatSession import ChatSession

app = Flask(__name__)

last_processed_response = None
response_ready = False
response_acknowledged = False

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Chatbot is up"})

@app.route('/chat', methods=['POST'])
def chat():
    global last_processed_response, response_ready, response_acknowledged
    data = request.get_json()
    user_input = data.get('user_input', '')

    if not user_input:
        return jsonify({"error": "No user_input provided."}), 400

    response = f"Simulated response to: {user_input}"
    last_processed_response = response
    response_ready = True
    response_acknowledged = False

    return jsonify({"response": response, "status": "processed"})

@app.route('/get-response', methods=['GET'])
def get_response():
    global response_ready, last_processed_response
    if response_ready:
        return jsonify({
            "response": last_processed_response,
            "status": "ready"
        })
    else:
        return jsonify({"status": "not_ready"})

@app.route('/confirm-receipt', methods=['POST'])
def confirm_receipt():
    global response_acknowledged, response_ready
    data = request.get_json()
    ack = data.get("ack", False)

    if ack:
        response_acknowledged = True
        response_ready = False
        return jsonify({"status": "acknowledged"})

    return jsonify({"error": "No acknowledgment received"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)