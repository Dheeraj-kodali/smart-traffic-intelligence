from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from datetime import datetime, timedelta
import tempfile
import os
import cv2

import pandas as pd

from src.detection.application.ports.detector_port import VehicleDetectorPort
from src.detection.infrastructure.video_io.frame_reader import VideoFrameReader
from src.detection.domain.entities.vehicle import DetectedVehicle
from PIL import Image


def get_congestion_level(count: int) -> str:
	if count <= 10:
		return "LOW"
	if count <= 25:
		return "MEDIUM"
	if count <= 50:
		return "HIGH"
	return "SEVERE"


@dataclass(frozen=True)
class TrafficVideoAnalysisResult:
	dataframe: pd.DataFrame
	output_csv_path: Path
	total_frames: int
	total_frames_processed: int
	average_vehicles_per_frame: float
	maximum_vehicles_in_frame: int
	peak_traffic_frame: int
	total_vehicles_detected: int
	background_image: Image.Image | None = None
	aggregated_detections: tuple[DetectedVehicle, ...] = ()


class AnalyzeVideoTrafficUseCase:
	def __init__(self, detector: VehicleDetectorPort, frame_reader: VideoFrameReader, output_csv_path: Path) -> None:
		self.detector = detector
		self.frame_reader = frame_reader
		self.output_csv_path = Path(output_csv_path)

	def execute(
		self,
		video_path: Path,
		confidence_threshold: float | None = None,
		frame_skip: int = 10,
		progress_callback: Callable[[int, int], None] | None = None,
	) -> TrafficVideoAnalysisResult:
		processed_video_path = video_path
		temp_file_path = None

		# 1. Detect the uploaded video's resolution
		cap = cv2.VideoCapture(str(video_path))
		width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

		# 2. If width > 1280 or height > 720:
		if width > 1280 or height > 720:
			# Downscale the video to 1280x720 while preserving aspect ratio
			scale = min(1280 / width, 720 / height)
			new_width = int(width * scale)
			new_height = int(height * scale)

			# 3. Save the resized video to a temporary file
			temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_file_path = temp_file.name
			temp_file.close()

			fourcc = cv2.VideoWriter_fourcc(*'mp4v')
			out = cv2.VideoWriter(temp_file_path, fourcc, fps, (new_width, new_height))

			while True:
				ret, frame = cap.read()
				if not ret:
					break
				resized_frame = cv2.resize(frame, (new_width, new_height))
				out.write(resized_frame)
			out.release()
			processed_video_path = Path(temp_file_path)
		cap.release()

		rows: list[dict[str, int | str]] = []
		total_frames = self.frame_reader.count_frames(processed_video_path)
		total_vehicles_detected = 0
		background_image = None
		all_detections = []

		# 4. Run YOLO on the resized video (processed_video_path)
		for frame in self.frame_reader.iter_frames(processed_video_path, frame_skip=frame_skip):
			if background_image is None:
				background_image = frame.image.copy()
				
			detection_result = self.detector.detect(
				image=frame.image,
				source_name=f"{Path(video_path).stem}_frame_{frame.frame_number}",
				confidence_threshold=confidence_threshold,
			)
			total_count = detection_result.total_detections
			total_vehicles_detected += total_count
			all_detections.extend(detection_result.detections)
			
			# Synthesize timestamp (assume 30 FPS for demo)
			frame_timestamp = datetime.now() + timedelta(seconds=frame.frame_number / 30.0)
			
			rows.append(
				{
					"timestamp": frame_timestamp,
					"frame_number": frame.frame_number,
					"vehicle_count": total_count,
					"cars": detection_result.counts.get("car", 0),
					"trucks": detection_result.counts.get("truck", 0),
					"buses": detection_result.counts.get("bus", 0),
					"motorcycles": detection_result.counts.get("motorcycle", 0),
					"congestion_level": get_congestion_level(total_count),
				}
			)
			if progress_callback is not None:
				progress_callback(min(frame.frame_number, total_frames), total_frames)

		dataframe = pd.DataFrame(rows, columns=[
			"timestamp", "frame_number", "vehicle_count", "cars", "trucks", "buses", "motorcycles", "congestion_level"
		])
		
		# 5. Delete temporary files after processing
		if temp_file_path is not None and os.path.exists(temp_file_path):
			os.remove(temp_file_path)
			
		self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
		dataframe.to_csv(self.output_csv_path, index=False)

		total_frames_processed = int(len(dataframe))
		average_vehicles_per_frame = float(dataframe["vehicle_count"].mean()) if not dataframe.empty else 0.0
		maximum_vehicles_in_frame = int(dataframe["vehicle_count"].max()) if not dataframe.empty else 0
		peak_traffic_frame = int(dataframe.loc[dataframe["vehicle_count"].idxmax()]["frame_number"]) if not dataframe.empty else 0

		return TrafficVideoAnalysisResult(
			dataframe=dataframe,
			output_csv_path=self.output_csv_path,
			total_frames=total_frames,
			total_frames_processed=total_frames_processed,
			average_vehicles_per_frame=average_vehicles_per_frame,
			maximum_vehicles_in_frame=maximum_vehicles_in_frame,
			peak_traffic_frame=peak_traffic_frame,
			total_vehicles_detected=total_vehicles_detected,
			background_image=background_image,
			aggregated_detections=tuple(all_detections),
		)