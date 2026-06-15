<div align="center">

# 🚦 Traffic Copilot AI

### Smart Traffic Intelligence System

An AI-powered traffic analytics platform combining computer vision, forecasting, and voice interaction for intelligent congestion monitoring.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-FF4B4B?logo=streamlit)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13.0-green?logo=opencv)
![Prophet](https://img.shields.io/badge/Prophet-1.3.0-blueviolet)
![Plotly](https://img.shields.io/badge/Plotly-6.8.0-blueviolet)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

![Traffic Copilot Banner](assets/banner.png)

</div>

## 📸 Demo

| Dashboard | Detection |
|------------|------------|
| ![](assets/dashboard.png) | ![](assets/detection.png) |

| Forecasting | Voice Assistant |
|--------------|-----------------|
| ![](assets/forecast.png) | ![](assets/voice_assistant.png) |

## ✨ Key Features

* ✅ Real-time vehicle detection
* ✅ Image analytics
* ✅ Video analytics
* ✅ Traffic forecasting
* ✅ Congestion scoring
* ✅ Voice assistant
* ✅ Downloadable reports
* ✅ Smart city dashboard

## 🛠️ Technology Stack

| Category | Technologies |
| --- | --- |
| **Language** | Python 3.11 |
| **Frontend UI** | Streamlit |
| **Computer Vision** | YOLOv8 (Ultralytics), OpenCV |
| **Time-Series AI** | Prophet |
| **Audio Processing** | SpeechRecognition, pyttsx3, PyAudio |
| **Data Visualization** | Plotly, Pandas, NumPy |
| **Deployment** | Hugging Face Spaces |

<details>
<summary><b>📂 Project Structure</b></summary>

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

</details>

<details>
<summary><b>🚀 Installation</b></summary>

```bash
git clone https://github.com/Dheeraj-kodali/smart-traffic-intelligence.git
cd smart-traffic-intelligence

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

</details>

## 💻 Local Execution

Start the application locally using Streamlit:

```bash
streamlit run app/streamlit_app.py
```
This will start the local server, typically available at `http://localhost:8501`.

## 🎙️ Sample Voice Commands

Click the **Start Voice Assistant** button in the City Dashboard tab and try asking:

```text
What is the current traffic status?
When will traffic be low?
What is the congestion score?
What is the traffic trend?
When is the next peak traffic period?
```

## ☁️ Deployment (Hugging Face Spaces)

This application is fully compatible with **Hugging Face Spaces** (Streamlit SDK).

- **Entry Point**: The space uses `app/streamlit_app.py` as the main entry point.
- **System Dependencies**: Hugging Face automatically installs `packages.txt` (which provides `ffmpeg`, `libsm6`, `libxext6`, `portaudio19-dev`).
- **Python Dependencies**: Hugging Face installs `requirements.txt`. We use `opencv-python-headless` for cloud compatibility.
- **Limitations**: Hugging Face Spaces do not provide server-side microphone access or local speaker playback. The application will gracefully fall back and disable voice input/output automatically, but text-based queries will continue to function.

## 🔮 Future Roadmap

* [ ] Multi-camera support
* [ ] Live CCTV integration
* [ ] Accident detection
* [ ] Traffic signal optimization
* [ ] Mobile application
* [ ] Cloud notifications

## 👨‍💻 Author

**Dheeraj Kodali**

GitHub: https://github.com/Dheeraj-kodali

## 📄 License

This project is licensed under the MIT License.

## ⭐ Support

If you found this project useful, please consider starring the repository.
