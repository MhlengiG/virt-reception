from flask import Flask, request, jsonify
from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery
from ChatSession import ChatSession
from waitress import serve



app = Flask(__name__)

print("Initializing system, please wait...")

# Core components
intent_classifier = Classifier()
feature_extractor = FeatureExtractor("trained_spacy_ner_model")
db_query = DBQuery(
    host='127.0.0.1',
    user='root',
    password='Dortmund11!.',
    database='ukzn'
)
chatbot = ChatSession(intent_classifier, feature_extractor, db_query)

# Shared state (can be replaced by Redis or DB later)
last_user_input = None
last_response = None
response_ready = False
response_confirmed = False


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Response generator is running"})


@app.route('/chat', methods=['POST'])
def receive_from_subsystem1():
    global last_user_input, last_response, response_ready, response_confirmed

    try:
        data = request.get_json()
        user_input = data.get("user_input", "")

        if not user_input:
            return jsonify({"error": "No user_input provided"}), 400

        # Store raw input from Subsystem 1
        last_user_input = user_input
        response_ready = False
        response_confirmed = False

        # Process input
        response = chatbot.chat(user_input)

        # Store response for Subsystem 4 to fetch
        last_response = response
        response_ready = True

        # Acknowledge to Subsystem 1
        return jsonify({
            "status": "input_received",
            "message": f"Input from Subsystem 1 acknowledged: '{user_input}'"
        })

    except Exception as e:
        print(f"Error in /chat: {e}")
        return jsonify({"error": "Internal processing error"}), 500


@app.route('/get-response', methods=['GET'])
def send_to_subsystem4():
    global last_response, response_ready

    if response_ready:
        return jsonify({
            "status": "ready",
            "response": last_response
        })
    else:
        return jsonify({
            "status": "not_ready",
            "message": "Response still being processed or already acknowledged"
        })


@app.route('/confirm-receipt', methods=['POST'])
def confirm_from_subsystem4():
    global response_ready, response_confirmed

    data = request.get_json()
    ack = data.get("ack", False)

    if ack:
        response_ready = False
        response_confirmed = True
        return jsonify({"status": "response_confirmed"})

    return jsonify({"error": "No acknowledgment received"}), 400


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
