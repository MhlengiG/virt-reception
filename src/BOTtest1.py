from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery

class ChatSession:
    def __init__(self, intent_classifier, feature_extractor, db_query):
        self.intent_classifier = intent_classifier
        self.feature_extractor = feature_extractor
        self.db_query = db_query

    def chat(self, user_input):
        print(f"\n🧠 User: {user_input}")

        # Step 1: Predict intent
        intent = self.intent_classifier.predictor(user_input)
        print(f"🗂️ Detected intent: {intent}")

        # Step 2: Extract features (entities/slots)
        slots = self.feature_extractor.extract(user_input, intent)
        print(f"🔍 Extracted slots: {slots}")

        # Step 3: Query the database
        response = self.db_query.query(intent, slots)
        print(f"💬 Bot: {response}\n")

        return response


if __name__ == "__main__":
    # Step 0: Initialize components
    print("🔌 Initializing chatbot pipeline...")

    # Load your trained intent classifier
    intent_classifier = Classifier()  # must include a `.predict()` method

    # Load your trained NER model
    feature_extractor = FeatureExtractor("trained_spacy_ner_model")

    # Connect to your database
    db_query = DBQuery(
        host='127.0.0.1',
        user='root',
        password='Dortmund11!.',
        database='ukzn'
    )

    # Create chatbot session
    chatbot = ChatSession(intent_classifier, feature_extractor, db_query)

    # Interactive test loop
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Chatbot: Bye!")
            break
        chatbot.chat(user_input)
