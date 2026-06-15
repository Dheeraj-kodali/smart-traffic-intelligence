from __future__ import annotations

from pathlib import Path
import os
import tempfile

import streamlit as st
from PIL import Image
import plotly.express as px

from src.detection.application.use_cases.analyze_video_traffic import AnalyzeVideoTrafficUseCase
from src.detection.application.use_cases.detect_vehicles import DetectVehiclesUseCase
from src.detection.domain.entities.vehicle import TARGET_VEHICLE_CLASSES
from src.detection.infrastructure.video_io.frame_reader import VideoFrameReader
from src.detection.infrastructure.yolo.yolov8_detector import Yolov8VehicleDetector
from src.forecasting.application.use_cases.forecast_traffic import ForecastTrafficUseCase
from src.intelligence.application.use_cases.calculate_congestion import CalculateCongestionUseCase

OUTPUT_DIR = Path("data/processed/detection")
TRAFFIC_COUNTS_CSV = Path("reports/traffic_report.csv")

MODEL_OPTIONS = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]

CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Glassmorphism Metric Card styling */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease-in-out, border-color 0.2s;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(129, 140, 248, 0.4);
    box-shadow: 0 8px 32px 0 rgba(129, 140, 248, 0.1);
}

/* Customize buttons */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
}
div.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
}
</style>
"""


@st.cache_resource
def get_detector(model_path: str) -> Yolov8VehicleDetector:
	return Yolov8VehicleDetector(model_path=model_path)


def get_traffic_level_display(count: int) -> str:
	if count <= 5:
		return "🟢 Low"
	elif count <= 15:
		return "🟡 Medium"
	elif count <= 30:
		return "🟠 High"
	else:
		return "🔴 Severe"


def display_congestion_alert(level: str) -> None:
	level = level.upper()
	if level == "MEDIUM":
		st.info("🚦 Traffic building up.")
	elif level == "HIGH":
		st.warning("⚠️ Congestion warning.")
	elif level == "SEVERE":
		st.error("🚨 Critical congestion alert.")


def render_dashboard() -> None:
	st.header("🌍 Smart City Dashboard")
	st.write("Real-time traffic intelligence and congestion monitoring.")
	
	video_result = st.session_state.get("video_analysis_result")
	forecast_result = st.session_state.get("forecast_result")
	
	if video_result is None:
		st.info("👋 Welcome! Please run Video Analytics to populate the City Dashboard.")
	else:
		df = video_result.dataframe
		current_vehicles = int(df["vehicle_count"].iloc[-1]) if not df.empty else 0
		all_counts = df["vehicle_count"].tolist() if not df.empty else [0]
		
		intelligence_uc = CalculateCongestionUseCase()
		intel_result = intelligence_uc.execute(current_vehicles, all_counts)
		overall_congestion = intel_result.classification.upper()
		
		peak_veh = video_result.maximum_vehicles_in_frame
		congestion_score = (current_vehicles / peak_veh * 100) if peak_veh > 0 else 0.0
		
		peak_row = df.loc[df["vehicle_count"].idxmax()] if not df.empty else None
		if peak_row is not None and "timestamp" in peak_row and peak_row["timestamp"] is not None:
			try:
				peak_time_str = peak_row["timestamp"].strftime("%H:%M:%S")
			except AttributeError:
				import pandas as pd
				try:
					peak_time_str = pd.to_datetime(peak_row["timestamp"]).strftime("%H:%M:%S")
				except Exception:
					peak_time_str = str(peak_row["timestamp"])
		else:
			peak_time_str = "N/A"
		
		if len(df) > 1:
			import numpy as np
			x = np.arange(len(df))
			y = df["vehicle_count"].values
			z = np.polyfit(x, y, 1)
			slope = z[0]
			if slope > 0.05:
				trend = "⬆ Increasing"
			elif slope < -0.05:
				trend = "⬇ Decreasing"
			else:
				trend = "➡ Stable"
		else:
			trend = "➡ Stable"
		
		st.markdown("### Traffic Overview")
		dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)
		dash_col1.metric("Current Status", overall_congestion)
		dash_col2.metric("Traffic Trend", trend)
		dash_col3.metric("Congestion Score", f"{congestion_score:.1f}%")
		dash_col4.metric("Peak Time", peak_time_str)
		
		display_congestion_alert(intel_result.classification)
		st.info(f"**Recommendation:** {intel_result.recommendation}")
		
		st.divider()
		st.markdown("### Analytics & Forecast")
		row2_col1, row2_col2 = st.columns(2)
		
		with row2_col1:
			st.markdown("**Vehicle Distribution**")
			vid_counts = {
				"Car": int(df["cars"].sum() if "cars" in df.columns else 0),
				"Motorcycle": int(df["motorcycles"].sum() if "motorcycles" in df.columns else 0),
				"Bus": int(df["buses"].sum() if "buses" in df.columns else 0),
				"Truck": int(df["trucks"].sum() if "trucks" in df.columns else 0),
			}
			import pandas as pd
			import plotly.express as px
			
			vid_pie_data = [{"Vehicle Type": k, "Count": v} for k, v in vid_counts.items()]
			vid_pie_df = pd.DataFrame(vid_pie_data)
			
			if sum(vid_counts.values()) > 0:
				vid_fig_pie = px.pie(vid_pie_df, values='Count', names='Vehicle Type', hole=0.5)
				vid_fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
				st.plotly_chart(vid_fig_pie, use_container_width=True)
			else:
				st.info("No vehicles detected.")
		
		with row2_col2:
			st.markdown("**Forecast Summary**")
			if forecast_result is not None:
				if hasattr(forecast_result, "lowest_traffic_time"):
					st.metric("Lowest Traffic Time", forecast_result.lowest_traffic_time)
					st.metric("Lowest Predicted Vehicles", f"{forecast_result.lowest_traffic_value:.1f} vehicles")
					st.metric("Peak Traffic Time", forecast_result.peak_traffic_time)
					st.metric("Peak Predicted Vehicles", f"{forecast_result.peak_traffic_value:.1f} vehicles")
				else:
					st.metric("Expected Peak Traffic", f"{forecast_result.peak_prediction:.1f} vehicles")
					st.metric("Expected Average Traffic", f"{forecast_result.average_prediction:.1f} vehicles")
				if hasattr(forecast_result, "mape"):
					st.metric("Model Accuracy Error (MAPE)", f"{forecast_result.mape:.1f}%")
			else:
				st.warning("No forecast available. Generate one in the Video Analytics tab.")

		st.divider()
		st.subheader("🎙️ Traffic Voice Assistant")
		if st.button("Start Voice Assistant"):
			with st.spinner("Listening..."):
				try:
					from src.assistant.dashboard_voice_service import run_dashboard_voice_assistant
					command, response = run_dashboard_voice_assistant()
					
					error_messages = [
						"no speech detected.",
						"speech service is unavailable.",
						"i could not understand the audio."
					]
					
					if command.lower() in error_messages or command.lower().startswith("an error occurred"):
						st.error(command)
					else:
						st.success(f"You said: {command}")
						st.info(response)
				except Exception as e:
					st.error(f"Voice Assistant failed: {str(e)}")


def render_image_detection() -> None:
	st.header("Vehicle Detection MVP")
	st.write("Upload a traffic image to detect cars, buses, trucks, and motorcycles with YOLOv8.")
	model_path_img = st.selectbox(
		"YOLO model",
		options=MODEL_OPTIONS,
		index=2,
		key="img_model_select",
		help="Select the pretrained YOLOv8 model used for detection.",
	)
	confidence_threshold_img = st.slider(
		"Confidence threshold",
		min_value=0.1,
		max_value=1.0,
		value=0.25,
		step=0.05,
		key="img_conf_slider"
	)
	uploaded_file = st.file_uploader("Upload a traffic image", type=["jpg", "jpeg", "png", "webp"], key="image_uploader")
	
	if uploaded_file is None:
		st.info("Choose an image to run detection.")
	else:
		image = Image.open(uploaded_file).convert("RGB")
		st.subheader("Uploaded Image")
		st.image(image, use_container_width=True)

		# State tracking for image detection
		if "image_detection_run" not in st.session_state:
			st.session_state.image_detection_run = False
		if "image_detection_result" not in st.session_state:
			st.session_state.image_detection_result = None
		if "last_image_file_name" not in st.session_state:
			st.session_state.last_image_file_name = None

		# Reset state if new image uploaded
		if st.session_state.last_image_file_name != uploaded_file.name:
			st.session_state.image_detection_run = False
			st.session_state.image_detection_result = None
			st.session_state.last_image_file_name = uploaded_file.name

		if st.button("Run Detection", type="primary"):
			st.session_state.image_detection_run = True
			with st.spinner("Running YOLOv8 inference..."):
				use_case = DetectVehiclesUseCase(detector=get_detector(model_path_img), output_dir=OUTPUT_DIR)
				result = use_case.execute(
					image=image,
					source_name=uploaded_file.name,
					confidence_threshold=confidence_threshold_img,
				)
				st.session_state.image_detection_result = result

		if st.session_state.image_detection_run:
			result = st.session_state.image_detection_result
			if result is not None:
				st.success("Detection completed successfully.")
				st.write("")
				
				current_level_display = get_traffic_level_display(result.total_detections)
				st.markdown(f"### Current Traffic Level: **{current_level_display}**")
				
				intelligence_uc = CalculateCongestionUseCase()
				intel_result = intelligence_uc.execute(result.total_detections, [result.total_detections])
				st.info(f"**Recommendation:** {intel_result.recommendation}")
				display_congestion_alert(intel_result.classification)

				st.subheader("Executive Dashboard")
				kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
				
				total_veh = result.total_detections
				avg_veh = float(result.total_detections)
				peak_veh = result.total_detections
				current_veh = result.total_detections
				congestion_score = (current_veh / peak_veh * 100) if peak_veh > 0 else 0.0
				
				kpi1.metric("🚗 Total Vehicles", total_veh)
				kpi2.metric("📊 Average Vehicles", f"{avg_veh:.1f}")
				kpi3.metric("📈 Peak Vehicles", peak_veh)
				kpi4.metric("⏱️ Current Vehicles", current_veh)
				kpi5.metric("🚨 Congestion Score", f"{congestion_score:.1f}%")

				st.write("---")

				st.subheader("Detection Summary")
				st.write(f"Model: **{model_path_img}**")
				st.write(f"Confidence threshold: **{confidence_threshold_img:.2f}**")
				st.write(f"Raw detections before filtering: **{result.raw_detection_count}**")
				st.write(f"Detections removed by filtering: **{result.raw_detection_count - result.total_detections}**")
				st.write(f"Total vehicles detected: **{result.total_detections}**")

				st.subheader("Vehicle Type Analytics")
				
				total_det = result.total_detections if result.total_detections > 0 else 1
				
				import pandas as pd
				import plotly.express as px
				
				pie_data = []
				for label in TARGET_VEHICLE_CLASSES:
					count = result.counts.get(label, 0)
					pct = (count / total_det) * 100
					pie_data.append({"Vehicle Type": label.title(), "Count": count, "Percentage": f"{pct:.0f}%"})
					
				pie_df = pd.DataFrame(pie_data)
				
				col1, col2 = st.columns([1, 2])
				with col1:
					for idx, row in pie_df.iterrows():
						st.metric(f"{row['Vehicle Type']}s", f"{row['Percentage']}", delta=f"{row['Count']} vehicles", delta_color="off")
						
				with col2:
					if result.total_detections > 0:
						fig_pie = px.pie(pie_df, values='Count', names='Vehicle Type', hole=0.4)
						st.plotly_chart(fig_pie, use_container_width=True)
					else:
						st.info("No vehicles detected to show distribution.")
				st.write("")

				st.subheader("Visualization Options")
				vis_mode = st.radio(
					"Select Overlay Mode",
					options=["Show Bounding Boxes", "Show Heatmap", "Show Both"],
					horizontal=True,
					key="img_vis_mode"
				)

				from src.detection.infrastructure.visualization import generate_heatmap_overlay

				st.subheader("Output")
				if result.original_image is not None:
					if vis_mode == "Show Bounding Boxes":
						st.image(result.annotated_image, use_container_width=True)
					elif vis_mode == "Show Heatmap":
						heatmap_img = generate_heatmap_overlay(result.original_image, result.detections)
						st.image(heatmap_img, use_container_width=True)
					elif vis_mode == "Show Both":
						combined_img = generate_heatmap_overlay(result.annotated_image, result.detections)
						st.image(combined_img, use_container_width=True)
				else:
					st.image(result.annotated_image, use_container_width=True)

				if result.saved_path is not None and result.saved_path.exists():
					st.write("")
					with result.saved_path.open("rb") as file_handle:
						st.download_button(
							"Download Annotated Image",
							data=file_handle.read(),
							file_name=result.saved_path.name,
							mime="image/png",
						)
					st.success(f"Annotated image saved to {result.saved_path.as_posix()}")


def render_video_analytics() -> None:
	st.header("Traffic Video Analytics")
	st.write("Upload a traffic video to process frames with the same vehicle detector and generate per-frame counts.")
	
	model_path_vid = st.selectbox(
		"YOLO model",
		options=MODEL_OPTIONS,
		index=2,
		key="vid_model_select",
		help="Select the pretrained YOLOv8 model used for detection.",
	)
	confidence_threshold_vid = st.slider(
		"Confidence threshold",
		min_value=0.1,
		max_value=1.0,
		value=0.25,
		step=0.05,
		key="vid_conf_slider"
	)

	uploaded_video = st.file_uploader("Upload a traffic video", type=["mp4", "avi", "mov"], key="video_uploader")
	
	if uploaded_video is None:
		st.info("Upload a traffic video to begin.")
	else:
		st.subheader("Uploaded Video")
		st.video(uploaded_video)

		frame_skip = st.slider(
			"Frame skip",
			min_value=1,
			max_value=60,
			value=10,
			step=1,
			help="Process one frame, then skip the next N-1 frames.",
		)

		# State tracking for video analysis
		if "video_analysis_run" not in st.session_state:
			st.session_state.video_analysis_run = False
		if "video_analysis_result" not in st.session_state:
			st.session_state.video_analysis_result = None
		if "last_video_file_name" not in st.session_state:
			st.session_state.last_video_file_name = None

		# Reset if new video uploaded
		if st.session_state.last_video_file_name != uploaded_video.name:
			st.session_state.video_analysis_run = False
			st.session_state.video_analysis_result = None
			st.session_state.last_video_file_name = uploaded_video.name

		if st.button("Analyze Video", type="primary", key="analyze_video_button"):
			st.session_state.video_analysis_run = True
			temp_path: Path | None = None
			try:
				import time
				start_time = time.perf_counter()
				
				status_text = st.empty()
				status_text.info("Reading video...")
				
				# Fix Windows file lock issue by writing and closing first!
				t_temp_start = time.perf_counter()
				with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_video.name).suffix) as temp_file:
					temp_file.write(uploaded_video.getvalue())
					temp_path = Path(temp_file.name)
				t_temp_end = time.perf_counter()
				print(f"[Stage: Reading video] Input: {uploaded_video.name} | Output: {temp_path} | Execution Time: {t_temp_end - t_temp_start:.4f}s")

				progress_bar = st.progress(0.0)
				progress_text = st.empty()

				status_text.info("Processing frames...")
				
				t_count_start = time.perf_counter()
				total_frames = VideoFrameReader().count_frames(temp_path)
				t_count_end = time.perf_counter()
				print(f"[Stage: Processing frames] Input: {temp_path} | Output: {total_frames} frames | Execution Time: {t_count_end - t_count_start:.4f}s")

				def update_progress(current_frame: int, total_frames: int):
					percent = current_frame / total_frames if total_frames > 0 else 1.0
					percent = min(max(percent, 0.0), 1.0)
					progress_bar.progress(percent)
					progress_text.text(f"Processing: frame {current_frame}/{total_frames} ({int(percent * 100)}%)")
					status_text.info(f"Running YOLO... (Frame {current_frame}/{total_frames})")

				with st.spinner(f"Processing video with a frame skip of {frame_skip}..."):
					video_use_case = AnalyzeVideoTrafficUseCase(
						detector=get_detector(model_path_vid),
						frame_reader=VideoFrameReader(),
						output_csv_path=TRAFFIC_COUNTS_CSV,
					)
					t_exec_start = time.perf_counter()
					video_result = video_use_case.execute(
						video_path=temp_path,
						confidence_threshold=confidence_threshold_vid,
						frame_skip=frame_skip,
						progress_callback=update_progress,
					)
					t_exec_end = time.perf_counter()
					print(f"[Stage: Running YOLO] Input: {temp_path} | Output: {video_result.total_frames_processed} frames processed | Execution Time: {t_exec_end - t_exec_start:.4f}s")

				status_text.info("Generating CSV...")
				t_csv_start = time.perf_counter()
				# CSV was generated internally by video_result, so we just log this stage
				t_csv_end = time.perf_counter()
				print(f"[Stage: Generating CSV] Input: {len(video_result.dataframe)} rows | Output: {TRAFFIC_COUNTS_CSV} | Execution Time: {t_csv_end - t_csv_start:.4f}s")

				status_text.success("Completed.")
				print(f"[Total Pipeline Time] Execution Time: {time.perf_counter() - start_time:.4f}s")
				st.session_state.video_analysis_result = video_result
			except Exception as e:
				st.error(f"Error during video processing: {e}")
			finally:
				if temp_path is not None and temp_path.exists():
					try:
						os.unlink(temp_path)
					except Exception:
						pass

		if st.session_state.video_analysis_run:
			video_result = st.session_state.video_analysis_result
			if video_result is not None:
				st.success("Video analysis completed successfully.")
				
				congestion_colors = {
					"LOW": "#2ecc71",
					"MEDIUM": "#f39c12",
					"HIGH": "#e74c3c",
					"SEVERE": "#8b0000"
				}
				
				df = video_result.dataframe
				current_vehicles = int(df["vehicle_count"].iloc[-1]) if not df.empty else 0
				all_counts = df["vehicle_count"].tolist() if not df.empty else [0]
				
				intelligence_uc = CalculateCongestionUseCase()
				intel_result = intelligence_uc.execute(current_vehicles, all_counts)
				overall_congestion = intel_result.classification.upper()

				current_level_display = get_traffic_level_display(current_vehicles)
				st.markdown(f"### Current Traffic Level: **{current_level_display}**")
				
				if len(df) > 1:
					import numpy as np
					x = np.arange(len(df))
					y = df["vehicle_count"].values
					z = np.polyfit(x, y, 1)
					slope = z[0]
					trendline = np.poly1d(z)(x)
					df["trendline"] = trendline
					if slope > 0.05:
						trend = "⬆ Increasing"
					elif slope < -0.05:
						trend = "⬇ Decreasing"
					else:
						trend = "➡ Stable"
				else:
					trend = "➡ Stable"
					df["trendline"] = df["vehicle_count"] if not df.empty else 0
				st.markdown(f"### Traffic Trend: **{trend}**")
				
				st.info(f"**Recommendation:** {intel_result.recommendation}")
				display_congestion_alert(intel_result.classification)
				
				if video_result.background_image is not None and len(video_result.aggregated_detections) > 0:
					st.subheader("Aggregated Traffic Density Heatmap")
					st.write("Visualizing overall traffic density across the entire video on the first frame.")
					from src.detection.infrastructure.visualization import generate_heatmap_overlay
					heatmap_img = generate_heatmap_overlay(video_result.background_image, video_result.aggregated_detections)
					st.image(heatmap_img, use_container_width=True)
				
				st.subheader("Executive Dashboard")
				kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
				
				df = video_result.dataframe
				peak_row = df.loc[df["vehicle_count"].idxmax()] if not df.empty else None
				
				if peak_row is not None and "timestamp" in peak_row and peak_row["timestamp"] is not None:
					try:
						peak_time_str = peak_row["timestamp"].strftime("%H:%M:%S")
					except AttributeError:
						import pandas as pd
						try:
							peak_time_str = pd.to_datetime(peak_row["timestamp"]).strftime("%H:%M:%S")
						except Exception:
							peak_time_str = str(peak_row["timestamp"])
				else:
					peak_time_str = "N/A"
				
				total_veh = video_result.total_vehicles_detected
				avg_veh = video_result.average_vehicles_per_frame
				peak_veh = video_result.maximum_vehicles_in_frame
				current_veh = current_vehicles
				congestion_score = (current_veh / peak_veh * 100) if peak_veh > 0 else 0.0
				
				kpi1.metric("🚗 Total Vehicles", total_veh)
				kpi2.metric("📊 Average Vehicles", f"{avg_veh:.1f}")
				kpi3.metric("📈 Peak Vehicles", peak_veh)
				kpi4.metric("🕒 Peak Time", peak_time_str)
				kpi5.metric("⏱️ Current Vehicles", current_veh)
				kpi6.metric("🚨 Congestion Score", f"{congestion_score:.1f}%")

				st.subheader("Analytics Dashboard")
				
				fig_line = px.line(df, x="frame_number", y=["vehicle_count", "trendline"], title="Traffic Trend Analysis", markers=True)
				if peak_row is not None:
					fig_line.add_scatter(x=[peak_row["frame_number"]], y=[peak_row["vehicle_count"]], mode="markers", marker=dict(size=15, color="red", symbol="star"), name="Peak Traffic")
				st.plotly_chart(fig_line, use_container_width=True)
				
				fig_bar = px.bar(df, x="frame_number", y="vehicle_count", color="congestion_level", 
								 title="Congestion Level Timeline", 
								 color_discrete_map=congestion_colors)
				st.plotly_chart(fig_bar, use_container_width=True)

				st.subheader("Vehicle Type Analytics")
				import pandas as pd
				vid_counts = {
					"Car": int(df["cars"].sum() if "cars" in df.columns else 0),
					"Motorcycle": int(df["motorcycles"].sum() if "motorcycles" in df.columns else 0),
					"Bus": int(df["buses"].sum() if "buses" in df.columns else 0),
					"Truck": int(df["trucks"].sum() if "trucks" in df.columns else 0),
				}
				total_vid_det = sum(vid_counts.values()) if sum(vid_counts.values()) > 0 else 1
				
				vid_pie_data = []
				for label, count in vid_counts.items():
					pct = (count / total_vid_det) * 100
					vid_pie_data.append({"Vehicle Type": label, "Count": count, "Percentage": f"{pct:.0f}%"})
					
				vid_pie_df = pd.DataFrame(vid_pie_data)
				
				v_col1, v_col2 = st.columns([1, 2])
				with v_col1:
					for idx, row in vid_pie_df.iterrows():
						st.metric(f"{row['Vehicle Type']}s", f"{row['Percentage']}", delta=f"{row['Count']} detections", delta_color="off")
						
				with v_col2:
					if sum(vid_counts.values()) > 0:
						vid_fig_pie = px.pie(vid_pie_df, values='Count', names='Vehicle Type', hole=0.4)
						st.plotly_chart(vid_fig_pie, use_container_width=True)
					else:
						st.info("No vehicles detected to show distribution.")

				st.subheader("Detailed Frame Counts")
				st.dataframe(df, use_container_width=True)

				st.divider()
				st.header("Traffic Forecasting Dashboard")
				horizon = st.selectbox("Select Forecast Horizon (Intervals)", [10, 30, 60], index=1)
				
				if st.button("Generate Forecast", type="primary"):
					with st.spinner(f"Training Prophet model for {horizon} intervals..."):
						try:
							st.write("---")
							st.write("**Forecast Debug Info**")
							st.write(f"Total rows passed to Prophet: {len(df)}")
							st.write(f"Unique timestamps: {df['timestamp'].nunique() if 'timestamp' in df.columns else 'N/A'}")
							st.write("First 5 rows:")
							st.dataframe(df.head())
							st.write("---")
							
							forecast_use_case = ForecastTrafficUseCase()
							forecast_result = forecast_use_case.execute(df, horizon=horizon)
							st.session_state.forecast_result = forecast_result
						except Exception as e:
							st.error(f"Forecast generation failed: {e}")
							st.stop()
						
				if "forecast_result" in st.session_state and st.session_state.forecast_result is not None:
					fr = st.session_state.forecast_result
					if fr.horizon == horizon:  # Ensure we show the right result
						st.subheader("Forecast Metrics")
						f_kpi1, f_kpi2, f_kpi3 = st.columns(3)
						f_kpi1.metric("Peak Predicted Traffic", f"{fr.peak_prediction:.1f} veh")
						f_kpi2.metric("Low Predicted Traffic", f"{fr.low_prediction:.1f} veh")
						f_kpi3.metric("Average Predicted Traffic", f"{fr.average_prediction:.1f} veh")
						
						import plotly.graph_objects as go
						fig = go.Figure()
						
						# Create business-friendly dataframe
						export_df = fr.forecast_df.copy()
						export_df = export_df.rename(columns={
							"ds": "timestamp",
							"yhat": "predicted_vehicle_count",
							"yhat_lower": "min_expected_vehicle_count",
							"yhat_upper": "max_expected_vehicle_count"
						})
						export_df["predicted_vehicle_count"] = export_df["predicted_vehicle_count"].round().astype(int)
						export_df["min_expected_vehicle_count"] = export_df["min_expected_vehicle_count"].round().astype(int)
						export_df["max_expected_vehicle_count"] = export_df["max_expected_vehicle_count"].round().astype(int)
						
						intelligence_uc = CalculateCongestionUseCase()
						max_forecast = export_df["predicted_vehicle_count"].max()
						
						# Apply intelligence layer rules
						results = export_df["predicted_vehicle_count"].apply(
							lambda x: intelligence_uc.evaluate_forecast(x, max_forecast)
						)
						
						export_df["traffic_level"] = [res[0] for res in results]
						export_df["congestion_score"] = [res[1] for res in results]
						export_df["recommendation"] = [res[2] for res in results]
						
						fig.add_trace(go.Scatter(x=fr.historical_df["timestamp"], y=fr.historical_df["vehicle_count"], mode="lines+markers", name="Historical", line=dict(color="#3b82f6")))
						if "moving_average" in fr.historical_df.columns:
							fig.add_trace(go.Scatter(x=fr.historical_df["timestamp"], y=fr.historical_df["moving_average"], mode="lines", name="Moving Average", line=dict(color="#f59e0b", dash="dash")))
						
						fig.add_trace(go.Scatter(x=export_df["timestamp"], y=export_df["predicted_vehicle_count"], mode="lines", name="Prophet Forecast", line=dict(color="#10b981")))
						
						fig.add_trace(go.Scatter(
							name='Upper Bound', x=export_df["timestamp"], y=export_df["max_expected_vehicle_count"],
							mode='lines', marker=dict(color="#444"), line=dict(width=0), showlegend=False
						))
						fig.add_trace(go.Scatter(
							name='Confidence Interval', x=export_df["timestamp"], y=export_df["min_expected_vehicle_count"],
							marker=dict(color="#444"), line=dict(width=0), mode='lines', fillcolor='rgba(16, 185, 129, 0.2)', fill='tonexty'
						))
						
						fig.update_layout(title="Traffic Forecast with Prophet", xaxis_title="Timestamp", yaxis_title="Vehicle Count")
						st.plotly_chart(fig, use_container_width=True)
						
						if hasattr(fr, 'eval_df') and fr.eval_df is not None:
							st.subheader("Forecast Evaluation Module")
							eval_col1, eval_col2, eval_col3 = st.columns(3)
							eval_col1.metric("MAE", f"{fr.mae:.2f}")
							eval_col2.metric("RMSE", f"{fr.rmse:.2f}")
							eval_col3.metric("MAPE", f"{fr.mape:.1f}%")
							
							eval_fig = px.line(fr.eval_df, x="timestamp", y=["actual_vehicle_count", "forecasted_vehicle_count"], title="Actual vs Forecasted Vehicle Count", markers=True)
							eval_fig.data[0].name = "Actual Count"
							if len(eval_fig.data) > 1:
								eval_fig.data[1].name = "Forecasted Count"
							st.plotly_chart(eval_fig, use_container_width=True)
						
						st.subheader("Detailed Forecast")
						st.dataframe(export_df, use_container_width=True)
						
						forecast_csv_path = Path("data/processed/traffic_forecasts.csv")
						forecast_csv_path.parent.mkdir(parents=True, exist_ok=True)
						export_df.to_csv(forecast_csv_path, index=False)
				
				st.divider()
				st.header("Data Export Center")
				st.write("Download your analytics reports below:")
				
				export_cols = st.columns(4)
				
				# 1. Vehicle Counts CSV
				counts_df = df[["timestamp", "cars", "motorcycles", "buses", "trucks"]].copy()
				export_cols[0].download_button("Download Vehicle Counts", data=counts_df.to_csv(index=False).encode('utf-8'), file_name="vehicle_counts.csv", mime="text/csv", use_container_width=True)
				
				# 2. Forecast CSV
				forecast_csv_path = Path("data/processed/traffic_forecasts.csv")
				if forecast_csv_path.exists():
					with forecast_csv_path.open("rb") as f:
						export_cols[1].download_button("Download Forecast", data=f.read(), file_name="traffic_forecasts.csv", mime="text/csv", use_container_width=True)
				else:
					export_cols[1].button("Download Forecast", disabled=True, use_container_width=True, help="Generate a forecast first.")
					
				# 3. Traffic Analytics CSV
				if video_result.output_csv_path.exists():
					with video_result.output_csv_path.open("rb") as f:
						export_cols[2].download_button("Download Analytics", data=f.read(), file_name="traffic_analytics.csv", mime="text/csv", use_container_width=True)
				else:
					export_cols[2].button("Download Analytics", disabled=True, use_container_width=True)
				
				# 4. PDF Report
				with export_cols[3]:
					if st.button("Generate PDF Report", use_container_width=True):
						with st.spinner("Generating..."):
							try:
								forecast_fig_bytes = fig.to_image(format="png", width=800, height=500) if 'fig' in locals() else None
							except Exception:
								forecast_fig_bytes = None
								
							pdf_path = Path("data/processed/traffic_report.pdf")
							pdf_path.parent.mkdir(parents=True, exist_ok=True)
							
							from src.detection.infrastructure.pdf_generator import generate_traffic_pdf_report
							summary_stats = {"Total Vehicles": str(total_veh), "Average Vehicles": f"{avg_veh:.1f}", "Peak Vehicles": str(peak_veh), "Current Vehicles": str(current_veh)}
							vehicle_counts = {"Cars": int(df["cars"].sum() if "cars" in df.columns else 0), "Buses": int(df["buses"].sum() if "buses" in df.columns else 0), "Trucks": int(df["trucks"].sum() if "trucks" in df.columns else 0), "Motorcycles": int(df["motorcycles"].sum() if "motorcycles" in df.columns else 0)}
							
							generate_traffic_pdf_report(pdf_path, summary_stats, vehicle_counts, overall_congestion, f"{congestion_score:.1f}%", f"Time: {peak_time_str}, Count: {peak_veh}", intel_result.recommendation, forecast_fig_bytes)
							st.session_state.report_generated = True
							st.session_state.report_path = pdf_path
							
				if st.session_state.get("report_generated", False) and "report_path" in st.session_state:
					report_path = st.session_state.report_path
					if report_path.exists():
						with report_path.open("rb") as f:
							st.download_button("Download Generated PDF Report", data=f.read(), file_name="traffic_report.pdf", mime="application/pdf")


def render_vehicle_detection_page() -> None:
	# Inject CSS for premium looks
	st.markdown(CSS_STYLE, unsafe_allow_html=True)

	st.title("Smart Traffic Intelligence")
	
	tab_dashboard, tab_image, tab_video = st.tabs([
		"🌍 City Dashboard",
		"📷 Image Detection",
		"🎥 Video Analytics"
	])
	
	with tab_dashboard:
		render_dashboard()

	with tab_image:
		render_image_detection()

	with tab_video:
		render_video_analytics()
