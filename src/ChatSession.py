from Classifier import Classifier
from FeatureExtractorClass import FeatureExtractor
from QueryDB import DBQuery

class ChatSession:
    def __init__(self, intent_classifier, feature_extractor, db_query):
        self.intent_classifier = intent_classifier
        self.feature_extractor = feature_extractor
        self.db_query = db_query

    def chat(self, user_input):

        # Step 1: Predict intent
        intent = self.intent_classifier.predictor(user_input)

        # Step 2: Extract features (entities/slots)
        slots = self.feature_extractor.extract(user_input, intent)

        # Step 3: Query the database
        response = self.db_query.query(intent, slots)

        return response

