from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL.Image import Image


TARGET_VEHICLE_CLASSES: tuple[str, ...] = ("car", "bus", "truck", "motorcycle")
TARGET_VEHICLE_CLASS_IDS: tuple[int, ...] = (2, 3, 5, 7)


@dataclass(frozen=True)
class DetectedVehicle:
	label: str
	confidence: float
	bbox_xyxy: tuple[float, float, float, float]


@dataclass(frozen=True)
class VehicleDetectionResult:
	detections: tuple[DetectedVehicle, ...]
	raw_detection_count: int
	counts: dict[str, int]
	annotated_image: Image
	source_name: str
	saved_path: Path | None = None
	original_image: Image | None = None

	@property
	def total_detections(self) -> int:
		return len(self.detections)
