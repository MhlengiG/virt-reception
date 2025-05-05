import numpy as np
import string
import pickle
import tensorflow as tf
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

class Classifier:
    def __init__(self, model_path="intent_lstm_model.h5", tokenizer_path="tokenizer.pkl", label_encoder_path="label_encoder.pkl", confidence_threshold=0.6):
        # Load model and preprocessing tools
        self.model = load_model(model_path)
        with open(tokenizer_path, "rb") as f:
            self.tokenizer = pickle.load(f)
        with open(label_encoder_path, "rb") as f:
            self.label_encoder = pickle.load(f)

        self.confidence_threshold = confidence_threshold
        self.max_len = 20  # Must match training time

    def pre_process_input(self, text):
        # Basic lemmatization & punctuation removal
        lemmatizer = WordNetLemmatizer()
        text_lower = text.lower()
        tokens = text_lower.split()
        tokens = [lemmatizer.lemmatize(word.strip(string.punctuation)) for word in tokens]
        return " ".join(tokens)

    def predictor(self, text):
        preprocessed_text = self.pre_process_input(text)
        seq = self.tokenizer.texts_to_sequences([preprocessed_text])
        padded = pad_sequences(seq, maxlen=self.max_len, padding='post')

        # Predict
        probs = self.model.predict(padded)[0]
        predicted_index = np.argmax(probs)
        confidence = probs[predicted_index]
        predicted_label = self.label_encoder.inverse_transform([predicted_index])[0]

        if confidence < self.confidence_threshold:
            print(f"⚠️ Low confidence ({confidence:.2f})")
            return None
        else:
            return predicted_label
            print( f"✅ Predicted Intent: {predicted_label} (Confidence: {confidence:.2f})" )
        
"""
def main():
    MyClassifier = Classifier()
    print(MyClassifier.predictor("Where is the control systems lesson?"))
    print(MyClassifier.predictor("Hi, where can i find the female restroom please."))
    print(MyClassifier.predictor("Is prof z available today?"))
    print(MyClassifier.predictor("Hey, When is proffesor Xu available?"))
    print(MyClassifier.predictor("Does proffesor Xu have a class right now?"))
    print(MyClassifier.predictor("Where is Walingos, Office"))
    print(MyClassifier.predictor("Hello, When is the Digi Comms tutorial?"))
    print(MyClassifier.predictor("Okay, When will Tapamo be free today?"))
    print(MyClassifier.predictor("When will registration Open?"))
    print(MyClassifier.predictor("Where is the Digi Comms Test?"))
    print(MyClassifier.predictor("When does the EE class start?"))
    print(MyClassifier.predictor("I'm looking for Proffesor Tapamo?"))
    print(MyClassifier.predictor("Where is the nearest emergency?"))
    print(MyClassifier.predictor("Is Xu currently available?"))
    print(MyClassifier.predictor("thanks, Where can i find proffesor Tapamo?"))
    print(MyClassifier.predictor("Okay Cool, When will i be able to see Proffesor Xu?"))
    print(MyClassifier.predictor("Okay great, thats it for now."))
    print(MyClassifier.predictor("Okay bye."))
    print(MyClassifier.predictor("Hello, I need assistance"))

if __name__ == "__main__":
    main()
"""

