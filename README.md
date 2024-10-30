# BatteryDet
This repository project implements the following three functions:
1. Using YOLOv8 to detect the presence status of battery packs and publish messages through Kafka middleware.
2. In the yolov8_cpp_infer folder, implement the inference of YOLOv8 model through C++.
3. In the HikRobotCamera folder, implement the detection of battery packs through the HIKVISION camera, based on the camera SDK provided by HIKVISION.

## Quick Start
1. Use the following command to clone the project:
```bash
git clone https://github.com/Zhao-Qihao/BatteryDet.git
cd BatteryDet
```
2. Install the required dependencies:
```bash
$ conda create -n  py38cu113 python=3.8
$ conda activate py38cu113
$ pip install torch==1.12.0+cu113 torchvision==0.13.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html
$ pip install -r requirements.txt
```
3. Prepare your Kafka environment.
Refer to this blog: [prepare Kafka environment](https://blog.csdn.net/m0_37903882/article/details/133893424?ops_request_misc=%257B%2522request%255Fid%2522%253A%25222A08B7D9-7C47-4C37-AF10-7A8F23B4B430%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=2A08B7D9-7C47-4C37-AF10-7A8F23B4B430&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-9-133893424-null-null.142^v100^pc_search_result_base2&utm_term=Ubuntu%E4%B8%8Bkafka%E7%8E%AF%E5%A2%83&spm=1018.2226.3001.4187)

4. Start the Kafka server:
* after the Kafka environment is ready, you can use the following command to start the Kafka server:
```bash
$ cd /path/to/your/Kafka
$ bin/zookeeper-server-start.sh config/zookeeper.properties
$ bin/kafka-server-start.sh config/server.properties
```
* run the following command to create an Kafka topicTOPIC_VISION_BATTERY_STATUS:
```bash
$ bin/kafka-topics.sh --create --topic TOPIC_VISION_BATTERY_STATUS --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```
5. Run the following command to start the detection program and publish the detection results through Kafka:
```bash
$ cd BatteryDet
$ python camera_infer_kafka.py
```
6. You can use the following command to start subscribing to the detection results:
```bash
$ python kafka_consumer.py
```

## File Directory Description
```bash
flietree
.
├── battery.yaml           ----configuration file
├── camera_infer_kafka.py  ----detection program using camera and publish results through Kafka
├── export.py              ----export model from pth to onnx
├── HikRobotCamera         ----camera SDK provided by HIKVISION
├── kafka_consumer.py      ----subscribing program
├── models                 ----model files
├── README.md
├── requirements.txt       ----required dependencies
├── script                 
├── video
├── video_infer_kafka.py   ----detection program using video and publish results through Kafka
├── YOLO_train.py          ----training program
├── yolov8_cpp_infer       ----inference program using C++
├── yolov8n.pt
└── yolov8s.pt
```

## HIkRobotCamera
If there is no camera on your device, or you wanna use other camera, you can refer to this folder. And the main file is camera_opencv.py. This code implement an image data convert from HikCamera format to opencv format and infer the detection code. 


## yolov8_cpp_infer
Here is an implement of the inference program written in C++, you can refer to this file to implement your own inference program.
1. Train your model with YOLO_train.py to get the pth file, and then run the export.py to get the onnx file
2. Replace your vedio path and model weight onnx file path in the main.cpp
3. Compile the code with the following command:
```bash
$ cd yolov8_cpp_infer

# Note that by default the CMake file will try to import the CUDA library to be used with the OpenCVs dnn (cuDNN) GPU Inference.
# If your OpenCV build does not use CUDA/cuDNN you can remove that import call and run the example on CPU.

$ mkdir build
$ cd build
$ cmake ..
$ make
$ ./Yolov8CPPInference
```
