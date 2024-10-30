from ultralytics import YOLO

# Load a model
model = YOLO("yolov8s.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data="battery.yaml", val=False, epochs=60, imgsz=640, device=[0], batch=16)  
                      #scale=0, translate=0, fliplr=0, mosaic=0, erasing=0, crop_fraction=0.1, auto_augment=False)