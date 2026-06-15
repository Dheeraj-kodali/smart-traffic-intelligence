---
title: Smart Traffic Interactive Assistant
emoji: 🚦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

<div align="center">

# Smart Traffic Intelligence System

**AI-powered traffic analytics platform using computer vision, forecasting, and voice interaction.**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B?logo=streamlit&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![Prophet](https://img.shields.io/badge/Prophet-Time%20Series-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?logo=huggingface&logoColor=000)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📖 Overview

The **Smart Traffic Intelligence System** is an advanced, production-ready AI application designed to transform raw traffic video feeds into actionable city-planning insights. By seamlessly combining state-of-the-art computer vision models, time-series forecasting, and an interactive voice assistant, this platform provides a comprehensive solution for monitoring, analyzing, and predicting urban traffic congestion.

Built for both local desktop environments and robust cloud deployments (including Hugging Face Spaces), it empowers decision-makers with real-time data, predictive trends, and hands-free conversational analytics.

---

## ✨ Key Features

- 🚗 **Real-time vehicle detection** using state-of-the-art YOLOv8 models
- 📊 **Video analytics dashboard** for comprehensive traffic flow visualization
- 🚦 **Congestion scoring** to intelligently classify current road conditions
- 📈 **Time-series forecasting** predicting future traffic peaks with Prophet
- 🎙️ **Voice assistant** with built-in browser speech recognition
- 🔊 **Browser-based text-to-speech** for conversational responses
- 📄 **PDF report generation** for sharing executive traffic summaries
- 🐳 **Docker deployment** for robust, containerized distribution
- 🤗 **Hugging Face compatibility** for immediate cloud availability

---

## 🛠️ Technology Stack

| Layer | Technologies |
| --- | --- |
| **Frontend UI** | Streamlit |
| **AI Models (Computer Vision)** | YOLOv8 (Ultralytics), OpenCV |
| **Time-Series Forecasting** | Prophet |
| **Data Processing** | Pandas, NumPy |
| **Data Visualization** | Plotly |
| **Voice & Audio** | SpeechRecognition, gTTS, streamlit-mic-recorder, pyttsx3, PyAudio |
| **Infrastructure & Deployment** | Docker, Hugging Face Spaces |

---

## 🏗️ System Architecture

```mermaid
flowchart TD

A[Traffic Video Upload] --> B[YOLOv8 Vehicle Detection]

B --> C[Vehicle Counts]

C --> D[Congestion Analytics]

C --> E[Historical Traffic Dataset]

E --> F[Prophet Forecasting]

D --> G[City Dashboard]

F --> G

G --> H[Voice Assistant]

H --> I[Speech-to-Text]

I --> J[Command Processor]

J --> K[Dashboard Insights]

K --> L[Text-to-Speech Response]
```

---

## 🔄 Application Workflow

```mermaid
sequenceDiagram

participant User
participant Dashboard
participant YOLO
participant Prophet
participant Voice

User->>Dashboard: Upload traffic video
Dashboard->>YOLO: Detect vehicles
YOLO-->>Dashboard: Vehicle counts
Dashboard->>Prophet: Forecast traffic
Prophet-->>Dashboard: Future predictions
User->>Voice: Ask a question
Voice-->>Dashboard: Parsed command
Dashboard-->>User: Spoken response
```

---

## 📂 Project Structure

```text
smart-traffic-intelligence/
├── app/
├── assets/
├── configs/
├── data/
├── notebooks/
├── scripts/
├── src/
│   ├── analytics/
│   ├── assistant/
│   ├── detection/
│   ├── forecasting/
│   └── common/
├── requirements.txt
├── Dockerfile
├── packages.txt
└── README.md
```

---

## 💻 Local Setup

```bash
git clone <repository-url>
cd smart-traffic-intelligence

python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

streamlit run app/streamlit_app.py
```

---

## 🐳 Docker Deployment

```bash
docker build -t smart-traffic-intelligence .

docker run -p 7860:7860 smart-traffic-intelligence
```

---

## ☁️ Hugging Face Deployment

### Deployment Steps:
1. Create a Docker Space on Hugging Face.
2. Connect your GitHub repository.
3. Deploy automatically using the provided Dockerfile.

**Important Note on Voice Integration:**
- Browser microphone access works only when users grant permission.
- Local desktop TTS libraries such as `pyttsx3` are unavailable in cloud environments.
- In Hugging Face, the application automatically uses browser microphone + `gTTS`.
- Local mode safely keeps `SpeechRecognition` + `pyttsx3` support unchanged.

---

## 🚀 Future Enhancements

- Multi-camera support
- Live CCTV streaming
- Edge deployment
- Traffic signal optimization
- LLM-powered conversational analytics
- Mobile dashboard

---

## 🤝 Contributors

* Kodali Dheeraj

---

## 📄 License

This project is licensed under the MIT License.
