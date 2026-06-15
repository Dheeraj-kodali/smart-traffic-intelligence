from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

from src.detection.domain.entities.vehicle import DetectedVehicle


def generate_heatmap_overlay(
	image: Image.Image,
	detections: tuple[DetectedVehicle, ...],
	alpha: float = 0.5,
	radius: int = 40
) -> Image.Image:
	"""
	Generates a traffic density heatmap overlay from bounding boxes.
	
	Args:
		image: The original image to overlay the heatmap on.
		detections: Tuple of detected vehicles with bounding boxes.
		alpha: Blending factor for the heatmap overlay (0.0 to 1.0).
		radius: Radius of the density blur.
		
	Returns:
		A PIL Image with the heatmap overlay applied.
	"""
	img_array = np.array(image.convert("RGB"))
	h, w = img_array.shape[:2]
	
	# Create empty single-channel heatmap
	heatmap = np.zeros((h, w), dtype=np.float32)
	
	for det in detections:
		x1, y1, x2, y2 = det.bbox_xyxy
		cx = int((x1 + x2) / 2)
		cy = int((y1 + y2) / 2)
		
		# Add a single density point at the center of each bounding box
		if 0 <= cx < w and 0 <= cy < h:
			heatmap[cy, cx] += 1.0
			
	# Apply Gaussian blur to spread the density
	blur_size = radius * 2 + 1
	heatmap = cv2.GaussianBlur(heatmap, (blur_size, blur_size), 0)
	
	# Normalize heatmap to 0-255
	max_val = np.max(heatmap)
	if max_val > 0:
		heatmap = (heatmap / max_val * 255).astype(np.uint8)
	else:
		heatmap = heatmap.astype(np.uint8)
		
	# Apply colormap
	heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
	
	# Create mask where heatmap is very low to keep original image visible
	mask = heatmap > 10
	
	# Overlay
	overlay = img_array.copy()
	overlay[mask] = cv2.addWeighted(img_array[mask], 1 - alpha, heatmap_color[mask], alpha, 0)
	
	return Image.fromarray(overlay)
