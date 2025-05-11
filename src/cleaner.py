import json
import spacy
from spacy.training import offsets_to_biluo_tags

# Load blank tokenizer model
nlp = spacy.blank("en")

# Paths
input_file = "gliner_training.jsonl"
clean_output = "gliner_training_cleaned.jsonl"
bad_output = "gliner_training_bad_examples.jsonl"

# Storage
cleaned, broken = [], []

# Process line-by-line
with open(input_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if not line.strip():
            continue
        record = json.loads(line)
        text = record["text"]
        spans = [(e["start"], e["end"], e["label"]) for e in record["entities"]]

        try:
            doc = nlp.make_doc(text)
            offsets_to_biluo_tags(doc, spans)
            cleaned.append(record)
        except ValueError as e:
            record["error"] = str(e)
            broken.append(record)

# Write cleaned data
with open(clean_output, "w", encoding="utf-8") as f:
    for item in cleaned:
        f.write(json.dumps(item) + "\n")

# Optionally log bad examples
with open(bad_output, "w", encoding="utf-8") as f:
    for item in broken:
        f.write(json.dumps(item) + "\n")

print(f"✅ CLEANED: {len(cleaned)}")
print(f"❌ MISALIGNED: {len(broken)}")
