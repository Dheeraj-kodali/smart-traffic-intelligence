from __future__ import annotations

from pathlib import Path

from PIL import Image

from src.detection.application.use_cases.detect_vehicles import DetectVehiclesUseCase
from src.detection.domain.entities.vehicle import DetectedVehicle, VehicleDetectionResult


class FakeVehicleDetector:
	def detect(
		self,
		image: Image.Image,
		source_name: str = "uploaded_image",
		confidence_threshold: float | None = None,
	) -> VehicleDetectionResult:
		return VehicleDetectionResult(
			detections=(
				DetectedVehicle(
					label="car",
					confidence=0.91,
					bbox_xyxy=(10.0, 12.0, 120.0, 140.0),
				),
			),
			raw_detection_count=1,
			counts={"car": 1, "bus": 0, "truck": 0, "motorcycle": 0},
			annotated_image=image.copy(),
			source_name=source_name,
		)


def test_execute_saves_annotated_image(tmp_path: Path) -> None:
	image = Image.new("RGB", (128, 128), color="white")
	use_case = DetectVehiclesUseCase(detector=FakeVehicleDetector(), output_dir=tmp_path)

	result = use_case.execute(image=image, source_name="traffic_scene.jpg")

	assert result.source_name == "traffic_scene.jpg"
	assert result.total_detections == 1
	assert result.counts["car"] == 1
	assert result.saved_path is not None
	assert result.saved_path.exists()
	assert result.saved_path.parent == tmp_path
	assert result.saved_path.suffix == ".png"
