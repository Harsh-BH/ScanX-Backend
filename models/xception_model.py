# models/xception_model.py

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.applications.xception import Xception

def load_xception_model(weights_path):
    # Load the base Xception model without the top layers
    base_model = Xception(weights=None, include_top=False, input_shape=(299, 299, 3))

    # Add custom layers on top
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    predictions = Dense(1, activation='sigmoid')(x)

    # Define the full model
    model = Model(inputs=base_model.input, outputs=predictions)

    # Load pre-trained weights
    model.load_weights(weights_path)

    return model
