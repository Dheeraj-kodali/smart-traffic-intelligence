from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image
from PIL import ImageDraw, ImageFont

try:
	from ultralytics import YOLO
except ImportError as exc:  # pragma: no cover - import-time dependency guard
	YOLO = None  # type: ignore[assignment]
	YOLO_IMPORT_ERROR = exc
else:
	YOLO_IMPORT_ERROR = None

from src.detection.domain.entities.vehicle import (
	DetectedVehicle,
	TARGET_VEHICLE_CLASS_IDS,
	TARGET_VEHICLE_CLASSES,
	VehicleDetectionResult,
)


class Yolov8VehicleDetector:
	def __init__(self, model_path: str = "yolov8m.pt", confidence_threshold: float = 0.25) -> None:
		if YOLO is None:
			raise RuntimeError(
				"ultralytics is required for vehicle detection. Install the project dependencies first."
			) from YOLO_IMPORT_ERROR
		self.model = YOLO(model_path)
		self.confidence_threshold = confidence_threshold

	def detect(
		self,
		image: Image.Image,
		source_name: str = "uploaded_image",
		confidence_threshold: float | None = None,
	) -> VehicleDetectionResult:
		image_rgb = image.convert("RGB")
		image_array = np.asarray(image_rgb)
		threshold = self.confidence_threshold if confidence_threshold is None else confidence_threshold
		results = self.model.predict(
			source=image_array,
			conf=threshold,
			verbose=False,
			device="cpu",
		)

		if not results:
			empty_counts = {label: 0 for label in TARGET_VEHICLE_CLASSES}
			return VehicleDetectionResult(
				detections=(),
				raw_detection_count=0,
				counts=empty_counts,
				annotated_image=image_rgb.copy(),
				source_name=source_name,
				original_image=image_rgb.copy(),
			)

		result = results[0]
		detections: list[DetectedVehicle] = []
		counts = {label: 0 for label in TARGET_VEHICLE_CLASSES}
		raw_detection_count = 0
		filtered_boxes: list[tuple[float, float, float, float, str, float]] = []

		boxes = getattr(result, "boxes", None)
		if boxes is not None and len(boxes):
			class_ids = boxes.cls.cpu().tolist()
			confidences = boxes.conf.cpu().tolist()
			coordinates = boxes.xyxy.cpu().tolist()
			names: Any = result.names
			raw_detection_count = len(class_ids)

			for class_id, confidence, bbox in zip(class_ids, confidences, coordinates):
				label = str(names[int(class_id)])
				if label not in TARGET_VEHICLE_CLASSES:
					continue
				counts[label] += 1
				filtered_boxes.append(
					(
						float(bbox[0]),
						float(bbox[1]),
						float(bbox[2]),
						float(bbox[3]),
						label,
						float(confidence),
					)
				)
				detections.append(
					DetectedVehicle(
						label=label,
						confidence=float(confidence),
						bbox_xyxy=(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])),
					)
				)

		annotated_image = self._draw_filtered_annotations(image_rgb.copy(), filtered_boxes)

		return VehicleDetectionResult(
			detections=tuple(detections),
			raw_detection_count=raw_detection_count,
			counts=counts,
			annotated_image=annotated_image,
			source_name=source_name,
			original_image=image_rgb.copy(),
		)

	def _draw_filtered_annotations(
		self,
		image: Image.Image,
		boxes: list[tuple[float, float, float, float, str, float]],
	) -> Image.Image:
		draw = ImageDraw.Draw(image)
		font = ImageFont.load_default()
		palette = {
			"car": (46, 204, 113),
			"bus": (52, 152, 219),
			"truck": (230, 126, 34),
			"motorcycle": (231, 76, 60),
		}

		for x1, y1, x2, y2, label, confidence in boxes:
			color = palette.get(label, (255, 215, 0))
			draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=3)
			text = f"{label} {confidence:.2f}"
			text_bbox = draw.textbbox((x1, y1), text, font=font)
			text_height = text_bbox[3] - text_bbox[1]
			text_width = text_bbox[2] - text_bbox[0]
			label_y1 = max(0, y1 - text_height - 6)
			label_y2 = label_y1 + text_height + 6
			label_x2 = x1 + text_width + 8
			draw.rectangle([(x1, label_y1), (label_x2, label_y2)], fill=color)
			draw.text((x1 + 4, label_y1 + 2), text, fill=(0, 0, 0), font=font)

		return image
