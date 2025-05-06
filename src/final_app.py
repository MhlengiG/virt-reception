from flask import Flask, request, jsonify
from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery
from ChatSession import ChatSession
from waitress import serve
import traceback



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
        data = request.get_json(force=True)
        print("RAW JSON:", data)

        user_input = data.get("user_input", "")
        if not user_input:
            print("No user_input provided.")
            return jsonify({"error": "No user_input provided"}), 400

        last_user_input = user_input
        response_ready = False
        response_confirmed = False

        response = chatbot.chat(user_input)
        last_response = response
        response_ready = True

        return jsonify({
            "status": "input_received",
            "message": f"Input from Subsystem 1 acknowledged: '{user_input}'"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {e}"}), 500



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
