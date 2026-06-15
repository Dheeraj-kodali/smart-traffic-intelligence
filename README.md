# 🚦 Traffic Copilot AI — Smart Traffic Intelligence System

An AI-powered traffic analytics platform combining computer vision, time-series forecasting, and voice interaction for intelligent congestion monitoring and prediction.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B?logo=streamlit)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13.0-green?logo=opencv)
![Prophet](https://img.shields.io/badge/Prophet-1.3.0-blueviolet)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## ✨ Features

- **Real-time vehicle detection using YOLOv8**: Accurate vehicle identification and counting.
- **Image and video analytics**: Support for static images and continuous video feeds.
- **Traffic congestion scoring**: Dynamic congestion index calculation based on frame volume.
- **Traffic forecasting using Prophet**: Time-series predictions for upcoming traffic volume.
- **Smart city dashboard**: Beautiful, intuitive Streamlit native UI.
- **Voice assistant with speech recognition and text-to-speech**: Query dashboard data using natural voice commands.
- **Downloadable reports and analytics**: Export findings for external review.

## 🏗️ System Architecture

The project relies on a modular, decoupled architecture following clean architectural principles:
- **Detection Module**: Wraps YOLOv8 to extract object counts and positions.
- **Intelligence & Analytics Module**: Calculates congestion metrics and formats data.
- **Forecasting Module**: Analyzes historical counts using Facebook Prophet to predict peaks and trends.
- **Assistant Module**: Orchestrates Speech-to-Text, intent parsing, Text-to-Speech, and LLM integrations.

## 🛠️ Technology Stack

| Category | Technologies |
| --- | --- |
| **Language** | Python |
| **Frontend UI** | Streamlit |
| **Computer Vision** | YOLOv8 (Ultralytics), OpenCV |
| **Time-Series AI** | Prophet |
| **Audio Processing** | SpeechRecognition, pyttsx3, PyAudio |
| **Data Processing** | Pandas, NumPy |
| **Deployment** | Hugging Face Spaces |

## 📂 Project Structure

```text
smart-traffic-intelligence/
├── app/                  # Streamlit UI layouts and pages
│   └── streamlit_app.py  # Application entry point
├── configs/              # YAML configuration files
├── docs/                 # Documentation and user guides
├── scripts/              # Training, evaluation, and deployment scripts
├── src/                  # Core domain logic
│   ├── analytics/        # KPI generation and metrics
│   ├── assistant/        # Voice assistant & LLM service
│   ├── common/           # Shared utilities and logging
│   ├── detection/        # YOLOv8 integration and vehicle logic
│   ├── forecasting/      # Prophet time-series models
│   └── intelligence/     # Congestion scoring
├── tests/                # Unit and integration tests
├── packages.txt          # System-level dependencies
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 🚀 Installation

Ensure you have Python 3.9+ installed.

```bash
git clone https://github.com/Dheeraj-kodali/smart-traffic-intelligence.git
cd smart-traffic-intelligence

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## 💻 Local Execution

Start the application locally using Streamlit:

```bash
streamlit run app/streamlit_app.py
```
This will start the local server, typically available at `http://localhost:8501`.

## 🎙️ Voice Assistant Usage

Click the **Start Voice Assistant** button in the City Dashboard tab and try asking:

- *"What is the current traffic status?"*
- *"When will traffic be low?"*
- *"What is the congestion score?"*
- *"What is the traffic trend?"*
- *"When is the next peak traffic period?"*

## ☁️ Deployment (Hugging Face Spaces)

This application is fully compatible with **Hugging Face Spaces** (Streamlit SDK).

- **Entry Point**: The space uses `app/streamlit_app.py` as the main entry point.
- **System Dependencies**: Hugging Face automatically installs `packages.txt` (which provides `ffmpeg`, `libsm6`, `libxext6`, `portaudio19-dev`).
- **Python Dependencies**: Hugging Face installs `requirements.txt`. We use `opencv-python-headless` for cloud compatibility.
- **Limitations**: Hugging Face Spaces do not provide server-side microphone access or local speaker playback. The application will gracefully fall back and disable voice input/output automatically, but text-based queries will continue to function.

## 📸 Screenshots

![Dashboard](assets/dashboard.png)
![Vehicle Detection](assets/detection.png)
![Forecasting](assets/forecast.png)
![Voice Assistant](assets/voice_assistant.png)

## 🔮 Future Enhancements

- Multi-camera support
- Live CCTV integration
- Traffic signal optimization
- Accident detection
- Mobile application
- Alert notifications

## 👨‍💻 Author

**Dheeraj Kodali**

GitHub: https://github.com/Dheeraj-kodali

## 📄 License

This project is licensed under the MIT License.
