import random
import spacy
from spacy.util import minibatch
from spacy.training.example import Example
import json

# Load training data from JSONL file
train_data = []
with open("gliner_training.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        text = record["text"]
        entities = [(ent["start"], ent["end"], ent["label"]) for ent in record["entities"]]
        train_data.append((text, {"entities": entities}))

# Load the model
nlp = spacy.load("en_core_web_sm")

# Set up the NER pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# Add all entity labels to the NER
for _, annotations in train_data:
    for start, end, label in annotations["entities"]:
        ner.add_label(label)

# Disable other pipes and start training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()

    epochs = 50
    for epoch in range(epochs):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=20)
        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            nlp.update(examples, drop=0.2, losses=losses)
        print(f"Epoch {epoch + 1} Losses: {losses}")

# Save the model to a folder after training
nlp.to_disk("trained_spacy_ner_model")
print("✅ Model saved to 'trained_spacy_ner_model'")


