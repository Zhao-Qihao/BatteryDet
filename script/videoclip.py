import cv2

# 视频路径
video_path = "/home/itachi/Desktop/Video_20241025103438462.avi"
output_path = "./Video_20241025103438462_clipped.avi"

# 打开视频文件
cap = cv2.VideoCapture(video_path)

# 获取视频的帧率和帧数
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

# 计算起始和结束帧
start_time = 130  # 第一分钟开始
end_time = frame_count   # 第二分钟结束
start_frame = int(start_time * fps)
end_frame = int(end_time * fps)

# 获取视频的宽度和高度
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 创建视频编写器
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# 读取并写入指定时间段的帧
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
current_frame = start_frame

while cap.isOpened() and current_frame < end_frame:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)
    current_frame += 1

# 释放资源
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video clipped and saved to {output_path}")