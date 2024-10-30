import cv2
from ultralytics import YOLO
from kafka import KafkaProducer
import json
import torch
print(torch.version.cuda)

# # 初始化Kafka生产者
# producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=lambda v: json.dumps(v).encode('utf-8')
# )

# # 定义要发布的主题
# topic_name = 'TOPIC_VISION_BATTERY_STATUS'

# # 发布消息
# def publish_message(producer, topic, status):
#     try:
#         # 创建消息内容，符合 {"status":1} 或 {"status":0} 格式
#         message = {"status": status}
#         producer.send(topic, value=message)
#         producer.flush()
#         print(f"Message published successfully: {message}")
#     except Exception as ex:
#         print(f"Exception in publishing message: {str(ex)}")

# 定义矩形的坐标
top_left_ori = (1050, 0)
bottom_right_ori = (3450, 3036)
ratio_h = 640 / 3036
ratio_w = 640 / 4024
top_left = (int(top_left_ori[0] * ratio_w), int(top_left_ori[1] * ratio_h))
bottom_right = (int(bottom_right_ori[0] * ratio_w), int(bottom_right_ori[1] * ratio_h))

# Load the YOLO model
model = YOLO("./models/battery_s640_1030.pt")

# Open the video file
video_path = "video/truck_battery.avi"
cap = cv2.VideoCapture(video_path)

# 处理视频帧
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 调整帧大小
    resized_frame = cv2.resize(frame, (640, 640))
    
    # 运行YOLO模型进行推理
    results = model(resized_frame, conf=0.5)
    annotated_frame = results[0].plot()

    # 获取检测框
    boxes = results[0].boxes.xyxy.cpu().numpy()

    cv2.rectangle(annotated_frame, top_left, bottom_right, (0, 255, 0), 2)
    
    # 显示带注释的帧
    cv2.imshow("Battery Inference", annotated_frame)
    
    
    # 判断电池是否在矩形区域内，初始状态为0（未到位）
    status = 0
    if len(boxes) > 0:
        for box in boxes:
            # 检查检测框是否完全在矩形内
            if box[0] > top_left[0] and box[2] < bottom_right[0]:
                status = 1  # 如果检测到电池在范围内，更新状态为1（已到位）
                break
    
    # 发布状态消息
    # publish_message(producer, topic_name, status)
    
    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
