import json
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Detect sofa
results = model.predict(
    source="images/sofa1.jpg",
    save=True
)

# Extract detection
for result in results:
    for box in result.boxes:

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        confidence = float(box.conf[0])

        cls = int(box.cls[0])

        label = model.names[cls]

        detection = {
            "object": label,
            "confidence": round(confidence, 3),
            "bbox": {
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2),
                "width": round(x2 - x1, 2),
                "height": round(y2 - y1, 2)
            }
        }

# Save JSON
import os

os.makedirs("output", exist_ok=True)
with open("outputs/detection.json", "w") as f:
    json.dump(detection, f, indent=4)

print("Detection JSON created successfully.")