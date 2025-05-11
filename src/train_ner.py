import random
import spacy
import json
from spacy.training.example import Example
from spacy.util import minibatch
from spacy.scorer import Scorer
from sklearn.model_selection import train_test_split

# Load your dataset (full)
with open("gliner_training.jsonl", "r", encoding="utf-8") as f:
    full_data = []
    for line in f:
        record = json.loads(line.strip())
        text = record["text"]
        entities = [(ent["start"], ent["end"], ent["label"]) for ent in record["entities"]]
        full_data.append((text, {"entities": entities}))

# Split into train/dev
train_data, dev_data = train_test_split(full_data, test_size=0.1, random_state=42)

# Load model
nlp = spacy.load("en_core_web_sm")

# Add or get NER pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# Register all labels
for _, annotations in train_data:
    for start, end, label in annotations["entities"]:
        ner.add_label(label)

# Train NER
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for epoch in range(50):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=20)
        for batch in batches:
            examples = []
            for text, ann in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, ann)
                examples.append(example)
            nlp.update(examples, drop=0.2, losses=losses)
        print(f"Epoch {epoch + 1} Losses: {losses}")

# Save trained model
nlp.to_disk("trained_spacy_ner_model")
print("✅ Model saved to 'trained_spacy_ner_model'")

# Eval on dev set
scorer = Scorer()
examples = []
for text, ann in dev_data:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, ann)
    examples.append(example)

results = scorer.score(examples)
print("\\n=== Evaluation Results ===")
print(results)
