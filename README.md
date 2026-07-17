# ScanX Backend

Flask + blockchain (Solidity/Hardhat) backend with face-detection models for ScanX.

## Overview

ScanX Backend is a Flask REST API that detects deepfakes in images and videos and classifies text as AI-generated or human-written. When media is uploaded, the API pins the file to IPFS (via Pinata), extracts faces with OpenCV, runs them through an Xception-based deepfake classifier, and stores the result in MongoDB against the uploader's wallet address. A companion `VideoService` Solidity smart contract (managed with Hardhat) lets users pay a tiered fee and permanently record each analysis — the IPFS file hash and detection result — on-chain, tying results to their Ethereum address.

## Features

- **Image & video deepfake detection** — `POST /predict` accepts an image or video plus a `userId` (MetaMask address), extracts faces, and returns a `Real`/`Fake` label with a confidence score and per-frame breakdown for videos.
- **Face extraction** — OpenCV Haar cascade (`haarcascade_frontalface_default.xml`) detects faces in images and samples one frame per second from videos.
- **Xception deepfake classifier** — a Keras/TensorFlow Xception model (299×299 input, sigmoid output) scores each face for manipulation.
- **Text classification** — `POST /text` classifies text as `AI-Generated` or `Student-Written` using a DistilBERT tokenizer and a TensorFlow SavedModel.
- **IPFS storage** — uploaded files are pinned to IPFS through the Pinata API; the returned hash is stored and can be recorded on-chain.
- **MongoDB persistence** — each analysis (file hash, prediction, confidence, face count, user address, timestamp) is saved; `GET /videos` returns all stored records.
- **On-chain records & payments** — the `VideoService` smart contract stores per-user video results (IPFS hash + result + timestamp), supports basic/standard/premium pricing tiers paid in ETH, and emits a `VideoUploaded` event.

## API Endpoints

| Method | Route       | Description                                                             |
|--------|-------------|-------------------------------------------------------------------------|
| GET    | `/`         | Serves a simple demo UI (`templates/index.html`).                       |
| POST   | `/predict`  | Analyze an uploaded image/video for deepfakes (`file` + `userId` form). |
| GET    | `/videos`   | Return all stored analysis records from MongoDB.                        |
| POST   | `/text`     | Classify JSON `{ "text": "..." }` as AI-generated or human-written.     |

## Tech Stack

- **API:** Python 3.9, Flask 3.0.3, Flask-CORS
- **Machine learning:** TensorFlow 2.17, Keras 3.6, OpenCV (`opencv-python`), NumPy, Hugging Face Transformers 4.45 (DistilBERT)
- **Database:** MongoDB via `pymongo`
- **File storage:** IPFS via the Pinata API
- **Blockchain:** Solidity (`^0.8.x`), Hardhat, ethers.js 5.7, `@nomiclabs/hardhat-ethers`, `@nomiclabs/hardhat-waffle`, `ethereum-waffle`, Chai
- **Containerization:** Docker (`python:3.9-slim`)

## Getting Started

### Prerequisites

- Python 3.9
- Node.js and npm (for the Hardhat/Solidity tooling)
- A MongoDB connection string
- A Pinata account (API key + secret)
- Trained model files (not included in the repo, see below)

### Model files

These are excluded via `.gitignore` and must be provided locally:

- `xception_deepfake_image_5o.h5` — Xception deepfake classifier weights (project root)
- `model_text/my_model` — TensorFlow SavedModel used for text classification

### Environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=<your MongoDB connection string>
PINATA_API_KEY=<your Pinata API key>
PINATA_SECRET_API_KEY=<your Pinata secret API key>

# Only needed for deploying the smart contract with Hardhat
QUICKNODE_HTTP_URL=<RPC endpoint>
PRIVATE_KEY=<deployer wallet private key>
```

### Installation

```bash
# Python dependencies
pip install -r requirements.txt

# Node dependencies (for the smart contract tooling)
npm install
```

### Running the Flask API

```bash
python app.py
```

The app starts on the default Flask development port (`http://127.0.0.1:5000`).

Alternatively, run it with Docker:

```bash
docker build -t scanx-backend .
docker run -p 5000:5000 --env-file .env scanx-backend
```

### Smart contract (Hardhat)

The Solidity source lives in `contracts/VideoService.sol`. Compile and deploy with Hardhat:

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network goerli
```

## Project Structure

```
.
├── app.py                    # Flask app: /predict, /videos, /text, / routes
├── requirements.txt          # Python dependencies
├── dockerfile                # Container image (python:3.9-slim)
├── models/
│   └── xception_model.py     # Xception model definition / weight loader
├── utils/
│   ├── face_extraction.py    # Face extraction from video (OpenCV Haar cascade)
│   ├── prediction.py         # Deepfake prediction over extracted faces
│   ├── pinata.py             # Upload files to IPFS via Pinata
│   └── text_predict.py       # DistilBERT-based text classification
├── templates/index.html      # Demo web UI
├── static/js/app.js          # Front-end for the demo UI
├── haarcascade_frontalface_default.xml  # OpenCV face detector
├── contracts/VideoService.sol           # On-chain video/result storage + tiered payments
├── scripts/deploy.js         # Hardhat deployment script
├── hardhat.config.js         # Hardhat config (Solidity + network settings)
└── package.json              # Node/Hardhat dependencies
```
