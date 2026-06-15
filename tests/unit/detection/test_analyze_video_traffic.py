from __future__ import annotations

from pathlib import Path

from PIL import Image

from src.detection.application.use_cases.analyze_video_traffic import AnalyzeVideoTrafficUseCase
from src.detection.domain.entities.vehicle import DetectedVehicle, VehicleDetectionResult
from src.detection.infrastructure.video_io.frame_reader import VideoFrame


class FakeFrameReader:
	def count_frames(self, video_path: Path) -> int:
		return 20

	def iter_frames(self, video_path: Path, frame_skip: int = 10):
		image = Image.new("RGB", (32, 32), color="white")
		for frame_number in range(1, 21, frame_skip):
			yield VideoFrame(frame_number=frame_number, image=image)


class FakeVehicleDetector:
	def detect(self, image: Image.Image, source_name: str = "uploaded_image", confidence_threshold: float | None = None) -> VehicleDetectionResult:
		return VehicleDetectionResult(
			detections=(
				DetectedVehicle(
					label="car",
					confidence=0.91,
					bbox_xyxy=(10.0, 12.0, 120.0, 140.0),
				),
			),
			counts={"car": 1, "bus": 0, "truck": 0, "motorcycle": 0},
			annotated_image=image.copy(),
			source_name=source_name,
			raw_detection_count=1,
		)


def test_execute_processes_every_tenth_frame(tmp_path: Path) -> None:
	use_case = AnalyzeVideoTrafficUseCase(
		detector=FakeVehicleDetector(),
		frame_reader=FakeFrameReader(),
		output_csv_path=tmp_path / "traffic_counts.csv",
	)

	result = use_case.execute(video_path=tmp_path / "sample.mp4", frame_skip=10)

	assert result.total_frames == 20
	assert result.total_frames_processed == 2
	assert list(result.dataframe["frame_number"]) == [1, 11]
	assert list(result.dataframe["vehicle_count"]) == [1, 1]
	assert result.output_csv_path.exists()
	lines = result.output_csv_path.read_text(encoding="utf-8").splitlines()
	assert lines[0] == "timestamp,frame_number,vehicle_count,cars,trucks,buses,motorcycles,congestion_level"
	assert len(lines) == 3
	assert ",1,1,1,0,0,0,LOW" in lines[1]
	assert ",11,1,1,0,0,0,LOW" in lines[2]