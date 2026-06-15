# Smart Traffic Intelligence System

## Project Overview
The Smart Traffic Intelligence System is a computer vision and AI-powered dashboard designed to analyze traffic video feeds. It uses YOLOv8 for vehicle detection, Prophet for traffic forecasting, and features a Voice Assistant for natural language querying of the dashboard's analytics.

## Features
- **Real-Time Video Analytics**: Process video feeds to detect and classify vehicles.
- **Congestion Intelligence**: Automatically score and classify road congestion.
- **Traffic Forecasting**: Predict future traffic peaks and lulls using historical models.
- **Voice Assistant**: Ask questions naturally using voice or text commands to receive dashboard insights.

## Installation Steps
1. Clone the repository.
2. Ensure you have Python 3.9+ installed.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) For audio/voice support on Linux/Windows, ensure system audio drivers (like `portaudio19-dev` on Linux) are installed for `PyAudio`.

## Local Execution
Run the Streamlit app from the project root:
```bash
streamlit run app/streamlit_app.py
```
This will start the local server, typically available at `http://localhost:8501`.

## Hugging Face Deployment Instructions
This application is fully compatible with Hugging Face Spaces (Streamlit SDK).

1. Create a new Streamlit Space on Hugging Face.
2. Upload the repository files.
3. The Space will automatically install the system dependencies defined in `packages.txt` (like `ffmpeg`, `libsm6`, `libxext6`, `portaudio19-dev`).
4. The Space will then install the Python dependencies defined in `requirements.txt`. Note that `opencv-python-headless` is used to ensure cloud compatibility without requiring GUI libraries.
5. Hugging Face Spaces do not provide server-side microphone access. The application will gracefully fall back and disable voice input automatically. You can still use the text-based LLM logic.
