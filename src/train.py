from ultralytics import YOLO

model = YOLO("yolov8n-seg.pt")

model.train(
    data="datasets/sofa1/data.yaml",
    epochs=100,
    imgsz=640,
    batch=8,
    project="runs",
    name="segment",
    exist_ok=True
)

print("Training Completed!")