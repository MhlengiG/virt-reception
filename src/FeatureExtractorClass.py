import spacy
import re

COMMON_MISSPELLINGS = {
    "proffesor": "professor",
    "proff": "prof",
    "lectur": "lecture",
    "tutourial": "tutorial",
    "availble": "available",
    "proffessor": "professor"
}

ROLE_NORMALIZATION = {
    "proffesor": "Prof.",
    "professor": "Prof.",
    "doctor": "Dr.",
    "prof": "Prof.",
    "dr": "Dr.",
    "mr": "Mr.",
    "ms": "Ms."
}

def correct_spelling(text):
    text = text.lower()
    for wrong, right in COMMON_MISSPELLINGS.items():
        text = text.replace(wrong, right)
    return text


import re


def normalize_titles(text: str) -> str:
    title_map = {
        r"\b(proff?essor|professor)\b": "Prof",
        r"\b(prof)\b": "Prof",
        r"\bdoctor\b": "Dr",
        r"\bdr\b": "Dr",
        r"\bdr\.\b": "Dr",
        r"\bclass\b": "lesson",
        r"\blecure\b": "lesson"
    }

    for pattern, replacement in title_map.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def clean_surname(surname_text):
    # Remove punctuation and possessive suffixes
    surname_text = re.sub(r"[?.']", "", surname_text).strip()
    surname_text = re.sub(r"’s$|s'$|s$", "", surname_text, flags=re.IGNORECASE)

    stopwords = {'available', 'present', 'now', 'currently', 'today'}
    words = surname_text.split()

    # Return the first non-stopword, fallback to the first word
    return next((word.capitalize() for word in words if word.lower() not in stopwords), surname_text.capitalize())


class FeatureExtractor:
    def __init__(self, ner_model_path="trained_spacy_ner_model"):
        self.nlp = spacy.load(ner_model_path)

    def extract(self, text, intent):
        text = correct_spelling(text)
        text = normalize_titles(text)
        print(text)
        if intent in ["greeting_query", "goodbye_query"]:
            return {}

        doc = self.nlp(text)
        slots = {}

        # Load NER predictions
        for ent in doc.ents:
            if ent.label_ not in slots:
                slots[ent.label_] = ent.text.strip()

        text_lower = text.lower()

        #  Backup regex
        if intent in ["staff_availability", "location_of"] and "surname" not in slots:
            match = re.search(r"(prof|dr|mr|ms)\.?\s+([\w’-]+)", text_lower)
            if match:
                slots.setdefault("person_role",
                                 ROLE_NORMALIZATION.get(match.group(1).lower(), match.group(1).capitalize() + "."))
                slots["surname"] = clean_surname(match.group(2))

        # Clean extracted surnames
        if "surname" in slots:
            slots["surname"] = clean_surname(slots["surname"])

        # Normalize roles
        if "person_role" in slots:
            role = slots["person_role"].lower().replace(".", "")
            slots["person_role"] = ROLE_NORMALIZATION.get(role, slots["person_role"])

        # Fallback: class_type (lecture, lab, etc.)
        if intent in ["location_of", "timetable_query"]:
            for word in ["lecture", "lab", "tutorial", "practical", "class"]:
                if word in text_lower and "class_type" not in slots:
                    slots["class_type"] = word
                    break

        # Fallback: room_type (office, lab, etc.)
        if intent == "location_of" and "room_type" not in slots:
            for pattern in ["female toilet", "male toilet", "consultation room", "office", "lab", "exit", "reception"]:
                if pattern in text_lower:
                    slots["room_type"] = pattern
                    break

        # Default: day
        if intent in ["timetable_query", "staff_availability"] and "day" not in slots:
            slots["day"] = "today"

        # Fallback: EECE FAQ topics
        if intent == "EECE_faq" and "faq_topic" not in slots:
            for keyword in ["registration", "academic record", "appeal", "exclusion"]:
                if keyword in text_lower:
                    slots["faq_topic"] = keyword
                    break

        return slots


def main():
        # Initialize your FeatureExtractor
        extractor = FeatureExtractor("trained_spacy_ner_model")

        # Test cases for 'location_of' intent
        test_sentences = [
            "Where is Dr. Naidoo's office?",
            "I’m looking for the robotics lab.",
            "Can you direct me to the female toilet?",
            "Where is the Software Engineering tutorial?",
            "Show me where Prof. Mkhize’s office is.",
            "Where is the exit near reception?",
            "Locate the AI lecture venue.",
            "Where is Ms. Zulu’s lab?",
            "Where’s the computer networks class?",
            "Direct me to the nearest male toilet.",
            "Can i speak to proffesor Xu?"
        ]

        print("🧪 Testing Feature Extraction for intent: location_of\n")
        for i, sentence in enumerate(test_sentences, 1):
            features = extractor.extract(sentence, intent="location_of")
            print(f"{i}. 💬 {sentence}")
            for key, val in features.items():
                print(f"   ➤ {key}: {val}")
            print()

if __name__ == "__main__":
    main()