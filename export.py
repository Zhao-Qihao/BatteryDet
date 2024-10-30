from ultralytics import YOLO

model = YOLO("yolov8s.pt") # Load a pretrained model
model.export(format='onnx', imgsz=640, opset=12)