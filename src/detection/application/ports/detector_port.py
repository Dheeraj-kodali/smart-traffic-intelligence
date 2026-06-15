from __future__ import annotations

from typing import Protocol

from PIL.Image import Image

from src.detection.domain.entities.vehicle import VehicleDetectionResult


class VehicleDetectorPort(Protocol):
	def detect(
		self,
		image: Image,
		source_name: str = "uploaded_image",
		confidence_threshold: float | None = None,
	) -> VehicleDetectionResult:
		"""Detect target vehicles in a single image and return an annotated result."""
