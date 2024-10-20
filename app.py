from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import cv2
import tempfile
import logging
from pymongo import MongoClient

from utils.face_extraction import extract_faces_from_video
from utils.prediction import predict_faces
from utils.pinata import upload_to_pinata  # Ensure this module exists and has upload_to_pinata function
from utils.text_predict import predict_text  # Ensure this module exists and has predict_text function

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB
mongo_uri = os.getenv('DATABASE_URL')
if not mongo_uri:
    logger.error("No DATABASE_URL found in environment variables.")
    raise ValueError("No DATABASE_URL found in environment variables.")

client = MongoClient(mongo_uri)
db = client['ScanX']  # Replace 'ScanX' with your actual database name
videos_collection = db['videos']

def extract_faces_from_image(image_path):
    """
    Extracts faces from an image using OpenCV's Haar Cascade.
    
    :param image_path: Path to the image file.
    :return: List of face images.
    """
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        logger.warning(f"Unable to load image: {image_path}")
        return []  # Return an empty list if the image can't be loaded

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the Haar Cascade face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)

    # Prepare a list to store extracted faces
    extracted_faces = []

    for (x, y, w, h) in faces:
        # Crop the face from the image
        face = image[y:y + h, x:x + w]
        extracted_faces.append(face)

    logger.info(f"Detected {len(extracted_faces)} face(s) in image: {image_path}")
    return extracted_faces

# Ensure an 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate the presence of 'file' and 'userId' in the request
        if 'file' not in request.files or 'userId' not in request.form:
            logger.warning("No file or user ID provided in the request.")
            return jsonify({'error': 'No file or user ID provided.'}), 400

        uploaded_file = request.files['file']
        user_id = request.form['userId']  # MetaMask public address

        if uploaded_file.filename == '':
            logger.warning("Empty filename received.")
            return jsonify({'error': 'Empty filename.'}), 400

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.filename)[1]) as tmp:
            file_path = tmp.name
            uploaded_file.save(file_path)
            logger.info(f"Uploaded file saved temporarily at {file_path}")

        start_time = time.time()

        # Upload the file to Pinata (IPFS)
        file_hash = upload_to_pinata(file_path)
        if not file_hash:
            os.remove(file_path)
            logger.error("Failed to upload file to IPFS via Pinata.")
            return jsonify({'error': 'Failed to upload file to IPFS.'}), 500

        logger.info(f"File uploaded to Pinata with IPFS hash: {file_hash}")

        # Determine file type based on extension
        file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
        is_video = False
        if file_extension in ['.mp4', '.avi', '.mov', '.webm', '.wmv']:  # Add more video formats as needed
            faces = extract_faces_from_video(file_path)
            is_video = True  # Mark that we are dealing with a video
            file_type = 'video'
        elif file_extension in ['.jpg', '.jpeg', '.png']:  # Add more image formats as needed
            faces = extract_faces_from_image(file_path)
            is_video = False
            file_type = 'image'
        else:
            os.remove(file_path)
            logger.warning("Unsupported file format uploaded.")
            return jsonify({'error': 'Unsupported file format. Please upload an image or video.'}), 400

        if not faces:
            os.remove(file_path)
            logger.warning("No faces detected in the uploaded file.")
            return jsonify({'error': 'No faces detected in the file.'}), 400

        # Predict using the model
        predictions = predict_faces(faces, is_video)

        # Extract confidence values from predictions
        confidence_values = [pred['confidence'] for pred in predictions]

        # Ensure there are confidence values to calculate
        if len(confidence_values) == 0:
            avg_prediction = 0
        else:
            avg_prediction = sum(confidence_values) / len(confidence_values)

        # Convert average prediction to percentage
        confidence_percentage = avg_prediction * 100

        # Determine the label based on the average prediction
        threshold = 0.5  # Adjust this threshold based on your model's performance
        label = 'Real' if avg_prediction < threshold else 'Fake'

        processing_time = time.time() - start_time

        logger.info(f"Prediction completed: {label} with {confidence_percentage}% confidence in {processing_time} seconds.")

        # Response structure
        response = {
            'fileHash': file_hash,  # IPFS hash
            'prediction': label,
            'confidence': round(confidence_percentage, 2),
            'total_faces_analyzed': len(predictions),
            'processing_time': round(processing_time, 2),
            'details': []
        }

        # Include per-frame predictions if it's a video
        for pred in predictions:
            frame_info = {
                'frame_number': pred.get('frame_number', 'N/A') if is_video else 'N/A',
                'timestamp': round(pred['timestamp'], 2) if is_video else 'N/A',
                'confidence': round(pred['confidence'] * 100, 2)
            }
            response['details'].append(frame_info)

        # Store the result in MongoDB
        video_record = {
            'fileName': uploaded_file.filename,
            'fileHash': file_hash,  # Store IPFS hash
            'length': os.path.getsize(file_path) / 1000000,  # File size in MB
            'confidence': round(confidence_percentage, 2),
            'prediction': label,
            'totalFaces': len(predictions),
            'processingTime': round(processing_time, 2),
            'userId': user_id,  # MetaMask public address
            'createdAt': time.strftime('%Y-%m-%d %H:%M:%S'),
            'fileType': file_type  # Add this line
        }

        try:
            result = videos_collection.insert_one(video_record)
            response['db_id'] = str(result.inserted_id)
            logger.info(f"Video record inserted into MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
            response['db_error'] = str(e)

        # Clean up uploaded file
        os.remove(file_path)
        logger.info(f"Temporary file {file_path} removed.")

        # Return the full response
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in /predict route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        # Retrieve all video records from MongoDB
        videos = videos_collection.find()
        # Convert MongoDB cursor to list and jsonify
        video_list = []
        for video in videos:
            video['_id'] = str(video['_id'])  # Convert ObjectId to string
            video_list.append(video)
        logger.info("Retrieved all video records from MongoDB.")
        return jsonify(video_list), 200
    except Exception as e:
        logger.error(f"Error retrieving videos from MongoDB: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/text', methods=['POST'])
def classify_text():
    """Endpoint for classifying text."""
    try:
        data = request.get_json()  # Get the JSON data from the request
        text = data.get("text", "")  # Extract the text field

        if text:
            result = predict_text(text)  # Call the predict function from utils
            return jsonify({"classification": result})  # Return the result as JSON
        else:
            return jsonify({"error": "No text provided"}), 400  # Return error if no text is provided
    except Exception as e:
        logger.error(f"Error in /text route: {e}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    print(app.url_map)  # For debugging, prints all the routes
    app.run(debug=True)
