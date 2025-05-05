import spacy

# Load your trained spaCy NER model
nlp = spacy.load("trained_spacy_ner_model")

# 20 test sentences
test_sentences = [
    "Where is the AI practical?",
    "I need the location of Dr. Naidoo’s office.",
    "Show me the timetable for computer networks lab.",
    "Is Prof. Dlamini in the building today?",
    "What time is the digital systems lecture?",
    "Find me the software engineering tutorial venue.",
    "I’m looking for Ms. Zulu’s lab.",
    "Where is the exit closest to the robotics lab?",
    "Tell me where the head of department’s office is.",
    "I want to go to the electronics practical.",
    "Do you know where Prof. Mkhize is teaching today?",
    "Where is the reception located?",
    "Point me to the nearest female toilet.",
    "Where is the Embedded Systems lecture today?",
    "Locate the Applied Maths class.",
    "Where is Mr. Khumalo’s consultation room?",
    "I need to find the Engineering lab.",
    "Where can I get help for registration issues?",
    "What venue is used for Physics tutorial?",
    "Can you direct me to the computer lab?"
]

# Process and print results
for i, sentence in enumerate(test_sentences, 1):
    doc = nlp(sentence)
    print(f"\n{i}. 🧾 Text: {sentence}")
    for ent in doc.ents:
        print(f"   ➤ {ent.text} ({ent.label_})")
