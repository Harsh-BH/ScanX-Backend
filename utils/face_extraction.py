# utils/face_extraction.py

import cv2

def extract_faces_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    faces = []

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # Default to 30 if FPS cannot be determined

    frame_count = 0
    frame_interval = int(fps)  # Analyze one frame per second

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate timestamp for the current frame
        timestamp = frame_count / fps  # Calculate timestamp in seconds

        if frame_count % frame_interval == 0:
            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            detected_faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            for (x, y, w, h) in detected_faces:
                face = frame[y:y+h, x:x+w]
                face = cv2.resize(face, (299, 299))
                faces.append({
                    'face_image': face,
                    'frame_number': frame_count,
                    'timestamp': round(timestamp, 2)
                })

        frame_count += 1

    cap.release()
    return faces
