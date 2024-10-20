from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import cv2

# Import utility functions from your custom modules
from utils.face_extraction import extract_faces_from_video
from utils.prediction import predict_faces
from utils.text_predict import preprocess_text, predict_text

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Ensure an 'uploads' directory exists for saving files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to extract faces from an image
def extract_faces_from_image(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        return []  # Return an empty list if the image can't be loaded

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
    
    extracted_faces = [image[y:y+h, x:x+w] for (x, y, w, h) in faces]
    
    return extracted_faces

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image and video upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'Empty filename.'}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(file_path)

    start_time = time.time()

    # Check the file extension
    file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
    is_video = False

    if file_extension in ['.mp4', '.avi', '.mov']:  # Video formats
        faces = extract_faces_from_video(file_path)
        is_video = True
    elif file_extension in ['.jpg', '.jpeg', '.png']:  # Image formats
        faces = extract_faces_from_image(file_path)
    else:
        os.remove(file_path)
        return jsonify({'error': 'Unsupported file format. Please upload an image or video.'}), 400

    if not faces:
        os.remove(file_path)
        return jsonify({'error': 'No faces detected in the file.'}), 400

    # Call the face prediction model
    predictions = predict_faces(faces, is_video)

    # Calculate confidence and make a decision
    confidence_values = [pred['confidence'] for pred in predictions]
    avg_prediction = sum(confidence_values) / len(confidence_values) if confidence_values else 0
    confidence_percentage = avg_prediction * 100

    # Determine label (Real/Fake) based on a threshold
    threshold = 0.5
    label = 'Real' if avg_prediction < threshold else 'Fake'

    processing_time = time.time() - start_time

    response = {
        'prediction': label,
        'confidence': round(confidence_percentage, 2),
        'total_faces_analyzed': len(predictions),
        'processing_time': round(processing_time, 2),
        'details': []
    }

    # Include per-frame details if analyzing a video
    for pred in predictions:
        frame_info = {
            'frame_number': pred.get('frame_number', None),
            'timestamp': pred.get('timestamp', None),
            'confidence': round(pred['confidence'] * 100, 2)
        }
        response['details'].append(frame_info)

    os.remove(file_path)  # Clean up the uploaded file

    return jsonify(response)

@app.route('/text', methods=['POST'])
def classify_text():
    """Endpoint for classifying text."""
    data = request.get_json()  # Get the JSON data from the request
    text = data.get("text", "")  # Extract the text field

    if text:
        result = predict_text(text)  # Call the predict function from utils
        return jsonify({"classification": result})  # Return the result as JSON
    else:
        return jsonify({"error": "No text provided"}), 400  # Return error if no text is provided

# Run the Flask app
if __name__ == '__main__':
    print(app.url_map)  # For debugging, prints all the routes
    app.run(debug=True)
