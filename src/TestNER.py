import spacy

# Load your trained spaCy NER model
nlp = spacy.load("trained_spacy_ner_model")

# 20 test sentences
test_sentences = [
    "Where is Prof. Ndlovu's office?",
    "When is the Digital Systems lecture?",
    "Is Dr. Moyo available right now?",
    "Where can I find the Control Systems lab?",
    "What time is the Data Structures tutorial?",
    "Can I meet Prof. Pillay today?",
    "Where is the female toilet in this building?",
    "Who is the lecturer for ENEL3DS?",
    "Where is room EE/3-16 located?",
    "Is Mr. Naidoo free for consultation today?",
    "Where does the Machine Learning class take place?",
    "Where is the emergency exit?",
    "Can you tell me when the ENEL3CS lab is scheduled?",
    "Where can I find the reception?",
    "What’s the availability status of Prof. Dlamini?",
    "Where do I go for the ENEL2ES practical?",
    "Is Ms. Khumalo currently present?",
    "Tell me where the academic office is.",
    "Where does Prof. Sibanda teach today?",
    "Where is the consultation room for final-year students?"
]



# Process and print results
for i, sentence in enumerate(test_sentences, 1):
    doc = nlp(sentence)
    print(f"\n{i}. Text: {sentence}")
    for ent in doc.ents:
        print(f"   -> {ent.text} ({ent.label_})")
