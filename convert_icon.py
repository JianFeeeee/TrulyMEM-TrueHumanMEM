#!/usr/bin/env python3
"""
转换PNG图标为ICO格式
"""

from PIL import Image

def convert_to_ico():
    """转换PNG为ICO"""
    # 打开PNG图片
    img = Image.open('trulymem_new_icon.png')

    # 转换为RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # 调整大小为256x256
    img = img.resize((256, 256), Image.Resampling.LANCZOS)

    # 创建不同尺寸的图标
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    # 保存为ICO
    img.save('trulymem_icon.ico', format='ICO', sizes=icon_sizes)
    print("ICO图标已创建: trulymem_icon.ico")

if __name__ == "__main__":
    convert_to_ico()
