from ultralytics import YOLO

# Load pretrained YOLO model
model = YOLO("yolov8n.pt")

# Run detection on one image
results = model.predict(
    source="images/sofa1.jpg",
    save=True
)
for result in results:
    for box in result.boxes:

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        confidence = float(box.conf[0])

        cls = int(box.cls[0])

        label = model.names[cls]

        width = x2 - x1
        height = y2 - y1

        print("Object :", label)
        print("Confidence :", round(confidence, 3))
        print("Bounding Box :", x1, y1, x2, y2)
        print("Width :", width)
        print("Height :", height)

print("Detection completed successfully!")