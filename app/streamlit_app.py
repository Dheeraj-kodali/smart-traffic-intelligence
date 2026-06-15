from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

# Ensure required directories exist for cloud environments
for d in ["data", "output", "reports"]:
	(PROJECT_ROOT / d).mkdir(exist_ok=True, parents=True)

from src.detection.presentation.adapters.streamlit_detection_adapter import render_vehicle_detection_page


def main() -> None:
	st.set_page_config(
		page_title="Smart Traffic Intelligence System",
		page_icon="🚦",
		layout="wide",
	)
	render_vehicle_detection_page()


if __name__ == "__main__":
	main()

