# utils/prediction.py

import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.xception import preprocess_input
from models.xception_model import load_xception_model

# Load the model (ensure the correct path to weights)
model = load_xception_model('xception_deepfake_image_5o.h5')

# utils/prediction.py

# utils/prediction.py

import cv2  # Make sure OpenCV is imported

def predict_faces(faces, is_video=False):
    predictions = []
    
    for idx, face in enumerate(faces):
        # If face is a dictionary (from video), extract the face image
        if is_video:
            face_image = face['face_image']
            frame_number = face['frame_number']
            timestamp = face['timestamp']
        else:
            face_image = face  # For images, face itself is the image array
            frame_number = None  # No frame number for images
            timestamp = None     # No timestamp for images
        
        # Resize the face image to (299, 299) as required by the Xception model
        face_image = cv2.resize(face_image, (299, 299))

        # Preprocess the face image
        x = img_to_array(face_image)
        x = preprocess_input(x)
        x = np.expand_dims(x, axis=0)
        
        # Predict the probability of being a deepfake
        prob = model.predict(x)[0][0]
        
        # Append prediction details
        predictions.append({
            'confidence': prob,
            'frame_number': frame_number,
            'timestamp': timestamp
        })
    
    return predictions

