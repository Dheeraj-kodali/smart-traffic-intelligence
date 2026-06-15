from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path

from PIL.Image import Image

from src.detection.application.ports.detector_port import VehicleDetectorPort
from src.detection.domain.entities.vehicle import VehicleDetectionResult


class DetectVehiclesUseCase:
	def __init__(self, detector: VehicleDetectorPort, output_dir: Path) -> None:
		self.detector = detector
		self.output_dir = Path(output_dir)

	def execute(
		self,
		image: Image,
		source_name: str = "uploaded_image",
		confidence_threshold: float | None = None,
	) -> VehicleDetectionResult:
		detection_result = self.detector.detect(
			image=image,
			source_name=source_name,
			confidence_threshold=confidence_threshold,
		)
		saved_path = self._save_annotated_image(detection_result.annotated_image, source_name)
		return replace(detection_result, saved_path=saved_path)

	def _save_annotated_image(self, annotated_image: Image, source_name: str) -> Path:
		self.output_dir.mkdir(parents=True, exist_ok=True)
		safe_name = Path(source_name).stem or "traffic_image"
		timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
		output_path = self.output_dir / f"{safe_name}_{timestamp}_annotated.png"
		annotated_image.save(output_path)
		return output_path
