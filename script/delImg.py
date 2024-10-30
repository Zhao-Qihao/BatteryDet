import os

# 定义文件夹路径
folder_path = '/sdc1/zqh/data/TruckBattery/images1015/train/images'

# 定义起始和结束编号
start = 1
end = 9

# 遍历指定范围内的文件并删除
for i in range(start, end + 1):
    filename = f"{i:01d}.jpg"
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        print(f"Deleting {filename}")
        os.remove(file_path)
    else:
        print(f"{filename} does not exist")