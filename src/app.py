from flask import Flask, request, jsonify
from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery
from ChatSession import ChatSession

app = Flask(__name__)

print("Initializing system, please wait...")
intent_classifier = Classifier()
feature_extractor = FeatureExtractor("trained_spacy_ner_model")
db_query = DBQuery(
    host='127.0.0.1',
    user='root',
    password='Dortmund11!.',
    database='ukzn'
)
chatbot = ChatSession(intent_classifier, feature_extractor, db_query)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Chatbot is up"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')

        if not user_input:
            return jsonify({"error": "No user_input provided."}), 400

        response = chatbot.chat(user_input)
        return jsonify({"response": response})

    except Exception as e:
        # LOG the error if you want
        print(f" Error occurred: {e}")
        return jsonify({
            "error": "Internal server error",
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
