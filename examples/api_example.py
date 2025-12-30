#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：使用 Python API 调用文本识别服务
"""

import sys
import os

# 添加父目录到路径，以便导入 ocr_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_service import TextRecognitionService


def example_single_image():
    """示例1: 识别单张图片"""
    print("=" * 60)
    print("示例 1: 识别单张图片")
    print("=" * 60)
    
    # 初始化服务
    service = TextRecognitionService(lang='ch', use_gpu=False)
    
    # 识别图片
    image_path = "your_image.jpg"  # 替换为你的图片路径
    
    # 如果图片不存在，跳过此示例
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请将 'your_image.jpg' 替换为实际的图片路径\n")
        return
    
    # 识别并保存结果
    results = service.recognize_text(image_path, output_file="output_single.txt")
    
    # 处理识别结果
    print(f"\n共识别到 {len(results)} 条文本")
    for i, result in enumerate(results, 1):
        print(f"\n文本 {i}:")
        print(f"  内容: {result['text']}")
        print(f"  置信度: {result['confidence']:.4f}")
    
    print("\n")


def example_batch_images():
    """示例2: 批量识别多张图片"""
    print("=" * 60)
    print("示例 2: 批量识别多张图片")
    print("=" * 60)
    
    # 初始化服务
    service = TextRecognitionService(lang='ch', use_gpu=False)
    
    # 准备图片列表
    image_paths = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
    ]
    
    # 过滤存在的图片
    existing_images = [img for img in image_paths if os.path.exists(img)]
    
    if not existing_images:
        print("没有找到可用的图片文件")
        print("请将图片路径替换为实际存在的文件\n")
        return
    
    # 批量识别
    all_results = service.recognize_batch(existing_images, output_dir="output/")
    
    # 汇总结果
    print(f"\n批量处理完成，共处理 {len(all_results)} 张图片")
    for image_path, results in all_results.items():
        print(f"  {image_path}: {len(results)} 条文本")
    
    print("\n")


def example_multilingual():
    """示例3: 多语言识别"""
    print("=" * 60)
    print("示例 3: 多语言识别")
    print("=" * 60)
    
    # 识别英文
    print("\n识别英文图片:")
    service_en = TextRecognitionService(lang='en', use_gpu=False)
    
    english_image = "english_text.jpg"
    if os.path.exists(english_image):
        service_en.recognize_text(english_image, output_file="output_english.txt")
    else:
        print(f"英文图片不存在: {english_image}\n")
    
    # 识别日文
    print("\n识别日文图片:")
    service_jp = TextRecognitionService(lang='japan', use_gpu=False)
    
    japanese_image = "japanese_text.jpg"
    if os.path.exists(japanese_image):
        service_jp.recognize_text(japanese_image, output_file="output_japanese.txt")
    else:
        print(f"日文图片不存在: {japanese_image}\n")


def example_custom_processing():
    """示例4: 自定义处理识别结果"""
    print("=" * 60)
    print("示例 4: 自定义处理识别结果")
    print("=" * 60)
    
    service = TextRecognitionService(lang='ch', use_gpu=False)
    
    image_path = "your_image.jpg"
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请将 'your_image.jpg' 替换为实际的图片路径\n")
        return
    
    # 识别图片（不保存到文件）
    results = service.recognize_text(image_path)
    
    # 自定义处理：提取高置信度的文本
    high_confidence_texts = [
        r['text'] for r in results if r['confidence'] > 0.9
    ]
    
    print(f"\n高置信度文本（>0.9）共 {len(high_confidence_texts)} 条:")
    for text in high_confidence_texts:
        print(f"  - {text}")
    
    # 自定义处理：将所有文本合并为一段
    full_text = " ".join([r['text'] for r in results])
    print(f"\n合并后的完整文本:\n{full_text}")
    
    # 保存自定义格式
    with open("custom_output.txt", "w", encoding="utf-8") as f:
        f.write("高置信度文本:\n")
        for text in high_confidence_texts:
            f.write(f"{text}\n")
        f.write(f"\n完整文本:\n{full_text}\n")
    
    print("\n自定义结果已保存到 custom_output.txt\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("PaddleOCR 文本识别服务 - 使用示例")
    print("=" * 60 + "\n")
    
    print("提示：请先准备好测试图片，并修改示例代码中的图片路径\n")
    
    # 运行示例（实际使用时取消注释）
    # example_single_image()
    # example_batch_images()
    # example_multilingual()
    # example_custom_processing()
    
    print("=" * 60)
    print("示例演示完成")
    print("=" * 60)
    print("\n使用说明：")
    print("1. 编辑此文件，将图片路径替换为实际的文件路径")
    print("2. 取消相应示例函数的注释")
    print("3. 运行: python3 examples/api_example.py")
    print("\n")


if __name__ == '__main__':
    main()
