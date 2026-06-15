from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
from PIL import Image


@dataclass(frozen=True)
class VideoFrame:
	frame_number: int
	image: Image.Image


class VideoFrameReader:
	def count_frames(self, video_path: Path) -> int:
		video_path = Path(video_path)
		if not video_path.exists():
			raise FileNotFoundError(f"Video file does not exist: {video_path}")

		capture = cv2.VideoCapture(str(video_path))
		if not capture.isOpened():
			raise ValueError(f"Unable to open video file: {video_path}")

		try:
			frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
			return max(frame_count, 0)
		finally:
			capture.release()

	def iter_frames(self, video_path: Path, frame_skip: int = 10) -> Iterator[VideoFrame]:
		video_path = Path(video_path)
		if not video_path.exists():
			raise FileNotFoundError(f"Video file does not exist: {video_path}")
		if frame_skip < 1:
			raise ValueError("frame_skip must be at least 1")

		capture = cv2.VideoCapture(str(video_path))
		if not capture.isOpened():
			raise ValueError(f"Unable to open video file: {video_path}")

		frame_number = 0
		try:
			while True:
				success = capture.grab()
				if not success:
					break
				frame_number += 1
				if (frame_number - 1) % frame_skip != 0:
					continue
				success, frame = capture.retrieve()
				if not success:
					break
				rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				yield VideoFrame(frame_number=frame_number, image=Image.fromarray(rgb_frame))
		finally:
			capture.release()