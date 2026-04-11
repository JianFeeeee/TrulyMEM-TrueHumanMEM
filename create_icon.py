#!/usr/bin/env python3
"""
创建TrulyMEM应用图标
"""

from PIL import Image, ImageDraw, ImageFont
import sys

def create_icon():
    """创建应用图标"""
    # 创建256x256的图标
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制圆形背景
    margin = 20
    draw.ellipse(
        [margin, margin, size-margin, size-margin],
        fill=(52, 152, 219, 255),  # 蓝色背景
        outline=(41, 128, 185, 255),
        width=3
    )

    # 绘制字母T和M
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    # 绘制文字
    text = "TM"
    # 获取文字边界框
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 计算文字位置（居中）
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10

    # 绘制白色文字
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # 保存为PNG
    img.save('trulymem_icon.png', 'PNG')
    print("图标已创建: trulymem_icon.png")

    # 转换为ICO格式
    try:
        # 创建不同尺寸的图标
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        for icon_size in icon_sizes:
            icon = img.resize(icon_size, Image.Resampling.LANCZOS)
            icons.append(icon)

        # 保存为ICO
        img.save('trulymem_icon.ico', format='ICO', sizes=icon_sizes)
        print("ICO图标已创建: trulymem_icon.ico")
    except Exception as e:
        print(f"创建ICO失败: {e}")
        print("请使用在线工具将PNG转换为ICO")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("需要安装Pillow库: pip install Pillow")
        sys.exit(1)
