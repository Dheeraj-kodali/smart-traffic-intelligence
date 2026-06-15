import cv2
import numpy as np
import sys

def main():
	# Create a video of size 640x480, 30 frames, 10 FPS
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter('tests/fixtures/sample.mp4', fourcc, 10.0, (640, 480))
	if not out.isOpened():
		print("Error: Could not open VideoWriter.")
		sys.exit(1)

	for i in range(30):
		frame = np.zeros((480, 640, 3), dtype=np.uint8)
		# Draw some background shapes
		cv2.putText(frame, f"Traffic Demo Frame {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
		# Draw moving green rectangle (simulate car)
		cv2.rectangle(frame, (100 + i * 5, 200), (180 + i * 5, 280), (46, 204, 113), -1)
		out.write(frame)

	out.release()
	print("Video created successfully at tests/fixtures/sample.mp4")

if __name__ == "__main__":
	main()
