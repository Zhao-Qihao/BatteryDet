import os
from pathlib import Path

def rename_images_in_folder(image_folder_path, label_folder_path):
    # 获取文件夹路径
    image_folder = Path(image_folder_path)
    label_folder = Path(label_folder_path)
    
    # 检查文件夹是否存在
    if not image_folder.exists() or not image_folder.is_dir():
        print(f"文件夹 {image_folder_path} 不存在或不是一个有效的文件夹")
        return
    if not label_folder.exists() or not label_folder.is_dir():
        print(f"文件夹 {label_folder_path} 不存在或不是一个有效的文件夹")
        return
    
    # 获取文件夹中的所有图像文件，保持原有顺序
    image_files = [f for f in image_folder.iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}]
    
    # 检查是否有图像文件
    if not image_files:
        print(f"文件夹 {image_folder_path} 中没有图像文件")
        return
    
    # 重命名图像文件和对应的标签文件
    for i, image_file in enumerate(image_files, start=1):
        base_name = 407 + i
        new_image_name = image_folder / f"{base_name}{image_file.suffix}"
        new_label_name = label_folder / f"{base_name}.txt"
        
        # 检查新文件名是否已存在
        if new_image_name.exists():
            # 递增文件名直到找到一个不存在的文件名
            counter = 1
            while new_image_name.exists():
                new_image_name = image_folder / f"{base_name}_{counter}{image_file.suffix}"
                new_label_name = label_folder / f"{base_name}_{counter}.txt"
                counter += 1
            
            print(f"新文件名 {new_image_name} 已存在，递增为 {new_image_name.name}")
        
        try:
            image_file.rename(new_image_name)
            print(f"重命名 {image_file.name} 为 {new_image_name.name}")
            
            # 找到对应的标签文件并重命名
            label_file = label_folder / (image_file.stem + '.txt')
            if label_file.exists():
                label_file.rename(new_label_name)
                print(f"重命名 {label_file.name} 为 {new_label_name.name}")
            else:
                print(f"未找到对应的标签文件 {label_file.name}")
        except PermissionError:
            print(f"无法重命名 {image_file.name}，权限不足")
        except Exception as e:
            print(f"无法重命名 {image_file.name}，错误: {e}")

# 示例用法
image_folder_path = '/home/itachi/Desktop/images'
label_folder_path = '/home/itachi/Desktop/labels'
rename_images_in_folder(image_folder_path, label_folder_path)