# utils.py

import tensorflow as tf
from transformers import DistilBertTokenizer
import numpy as np

# Load the tokenizer (assuming you used DistilBERT for tokenizing)
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Load the model from the .pb format
model = tf.saved_model.load('model_text/my_model')

# Inference function (signature) to make predictions
infer = model.signatures["serving_default"]

def preprocess_text(text):
    """Preprocess the input text using the DistilBERT tokenizer."""
    inputs = tokenizer(text, return_tensors='tf', truncation=True, padding=True)
    return inputs['input_ids'], inputs['attention_mask']

def predict_text(text):
    """Classify the input text as AI-generated or student-written."""
    input_ids, attention_mask = preprocess_text(text)

    # Perform inference
    predictions = infer(input_ids=input_ids, attention_mask=attention_mask)

    # Assuming the model returns logits
    logits = predictions['logits']  # Change 'logits' to the actual output tensor name
    probs = tf.nn.softmax(logits, axis=-1)

    # Get the predicted class (0 or 1)
    predicted_class = np.argmax(probs, axis=-1)

    # Interpret the prediction (assuming 0 = student-written, 1 = AI-generated)
    if predicted_class == 0:
        return "Student-Written"
    else:
        return "AI-Generated"
