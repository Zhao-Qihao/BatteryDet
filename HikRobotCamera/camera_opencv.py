import sys
import time
import numpy as np
import cv2
from MvCameraControl_class import *
from ultralytics import YOLO
from kafka import KafkaProducer
import json

class HikCamera:
    def __init__(self):
        self.cam = None
        self.running = False
        self.data_buf = None
        self.nPayloadSize = None
        self.model = YOLO("./models/battery_s640_1023.pt")
        # 定义矩形的坐标
        self.top_left_ori = (454, 0)
        self.bottom_right_ori = (1700, 1080)
        self.resize = (640, 640)
        self.ratio_h = self.resize[1] / 1080
        self.ratio_w = self.resize[0] / 1920
        self.top_left = (int(self.top_left_ori[0] * self.ratio_w), int(self.top_left_ori[1] * self.ratio_h))
        self.bottom_right = (int(self.bottom_right_ori[0] * self.ratio_w), int(self.bottom_right_ori[1] * self.ratio_h))
        # 定义kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        # 定义要发布的主题
        self.topic_name = 'TOPIC_VISION_BATTERY_STATUS'

        # 发布消息
    def publish_message(self, producer, topic, status):
        try:
            # 创建消息内容，符合 {"status":1} 或 {"status":0} 格式
            message = {"status": status}
            producer.send(topic, value=message)
            producer.flush()
            print(f"Message published successfully: {message}")
        except Exception as ex:
            print(f"Exception in publishing message: {str(ex)}")

    def convert_to_opencv(self, pData, stFrameInfo):
        """
        将图像数据转换为OpenCV格式
        """
        if stFrameInfo.enPixelType == PixelType_Gvsp_Mono8:
            # 黑白图像
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        elif stFrameInfo.enPixelType == PixelType_Gvsp_RGB8_Packed:
            # RGB格式
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth, 3))
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        elif stFrameInfo.enPixelType == PixelType_Gvsp_BayerRG8:
            # Bayer格式
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            return cv2.cvtColor(image, cv2.COLOR_BayerRG2BGR)

        elif stFrameInfo.enPixelType == PixelType_Gvsp_BayerGR8:
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            return cv2.cvtColor(image, cv2.COLOR_BayerGR2BGR)

        elif stFrameInfo.enPixelType == PixelType_Gvsp_BayerGB8:
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            return cv2.cvtColor(image, cv2.COLOR_BayerGB2BGR)

        elif stFrameInfo.enPixelType == PixelType_Gvsp_BayerBG8:
            data = np.frombuffer(pData, dtype=np.uint8)
            image = data.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth))
            return cv2.cvtColor(image, cv2.COLOR_BayerBG2BGR)

        else:
            return None

    def connect_camera(self):
        """
        连接相机并初始化参数
        """
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0 or deviceList.nDeviceNum == 0:
            print("未找到相机设备")
            return False

        self.cam = MvCamera()
        stDeviceList = cast(deviceList.pDeviceInfo[0],
                            POINTER(MV_CC_DEVICE_INFO)).contents

        ret = self.cam.MV_CC_CreateHandle(stDeviceList)
        if ret != 0:
            print("创建句柄失败")
            return False

        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            print("打开设备失败")
            return False

        # 获取payload size
        stParam = MVCC_INTVALUE()
        ret = self.cam.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            print("获取PayloadSize失败")
            return False
        self.nPayloadSize = stParam.nCurValue

        # 分配图像缓冲区
        self.data_buf = (c_ubyte * self.nPayloadSize)()

        # 设置触发模式为关闭
        ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", 2)
        ret = self.cam.MV_CC_SetEnumValue("GainAuto", 2)
        ret = self.cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 1)
        if ret != 0:
            print("设置触发模式失败")
            return False

        # 开始取流
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            print("开始取流失败")
            return False

        return True

    def start_streaming(self):
        """
        开始循环采集图像
        """
        if not self.connect_camera():
            return

        self.running = True
        frame_count = 0
        start_time = time.time()
        stFrameInfo = MV_FRAME_OUT_INFO_EX()

        try:
            while self.running:
                ret = self.cam.MV_CC_GetOneFrameTimeout(self.data_buf, self.nPayloadSize, stFrameInfo, 1000)
                if ret == 0:
                    # 帧率计算
                    frame_count += 1
                    if frame_count % 30 == 0:
                        current_time = time.time()
                        fps = 30 / (current_time - start_time)
                        start_time = current_time
                        print(f"当前帧率: {fps:.2f} FPS")

                    # 转换为OpenCV格式
                    frame = self.convert_to_opencv(self.data_buf, stFrameInfo)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    if frame is not None:                       
                        resized_frame = cv2.resize(frame, self.resize)
                        # 进行推理
                        results = self.model(resized_frame, conf=0.6)
                        annotated_frame = results[0].plot()

                        # 绘制预定义的矩形
                        cv2.rectangle(annotated_frame, self.top_left, self.bottom_right, (0, 255, 0), 2)
                        cv2.imshow("Battery Inference", annotated_frame)
                        # 获取检测框
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        
                        # 判断电池是否在矩形区域内，初始状态为0（未到位）
                        status = 0
                        if len(boxes) > 0:
                            for box in boxes:
                                # 检查检测框是否完全在矩形内
                                if box[0] > self.top_left[0] and box[2] < self.bottom_right[0] and box[1] > self.top_left[1] and box[3] < self.bottom_right[1]:
                                    status = 1  # 如果检测到电池在范围内，更新状态为1（已到位）
                                    break
                        
                        # 发布状态消息
                        self.publish_message(self.producer, self.topic_name, status)

                        # 检查是否按下'q'键退出
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                else:
                    print(f"获取图像失败: {ret}")

        finally:
            self.stop_streaming()

    def stop_streaming(self):
        """
        停止采集并清理资源
        """
        if self.cam:
            self.running = False
            self.cam.MV_CC_StopGrabbing()
            self.cam.MV_CC_CloseDevice()
            self.cam.MV_CC_DestroyHandle()
        cv2.destroyAllWindows()

    def save_image(self, image, filename):
        """
        保存图像
        """
        cv2.imwrite(filename, image)


def main():
    camera = HikCamera()
    try:
        camera.start_streaming()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        camera.stop_streaming()


if __name__ == "__main__":
    main()