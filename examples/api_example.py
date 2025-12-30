#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：使用 Python API 调用文本识别和翻译服务
"""

import sys
import os

# 添加父目录到路径，以便导入 ocr_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_service import TextRecognitionService


def example_single_image():
    """示例1: 识别单张图片（不翻译）"""
    print("=" * 60)
    print("示例 1: 识别单张图片（不翻译）")
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


def example_ocr_with_translation():
    """示例2: 识别日文图片并翻译成中文"""
    print("=" * 60)
    print("示例 2: 识别日文图片并翻译成中文")
    print("=" * 60)
    
    # 检查 API 密钥是否设置
    if not os.getenv('ARK_API_KEY'):
        print("警告: 未设置 ARK_API_KEY 环境变量")
        print("请先设置环境变量: export ARK_API_KEY='your-api-key'")
        print("跳过此示例\n")
        return
    
    # 初始化服务（启用翻译）
    service = TextRecognitionService(
        lang='japan',              # OCR 识别语言为日文
        use_gpu=False,
        enable_translation=True,   # 启用翻译功能
        source_lang='ja',          # 源语言：日文
        target_lang='zh'           # 目标语言：中文
    )
    
    # 识别图片
    image_path = "manga.jpg"  # 替换为你的日文图片路径
    
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请将 'manga.jpg' 替换为实际的日文图片路径\n")
        return
    
    # 识别并翻译，保存结果
    results = service.recognize_text(image_path, output_file="output_translated.txt")
    
    # 处理识别和翻译结果
    print(f"\n共识别并翻译 {len(results)} 条文本")
    for i, result in enumerate(results, 1):
        print(f"\n文本 {i}:")
        print(f"  原文: {result['text']}")
        if 'translated' in result:
            print(f"  译文: {result['translated']}")
            print(f"  翻译状态: {'成功' if result.get('translation_success', False) else '失败'}")
        print(f"  置信度: {result['confidence']:.4f}")
    
    print("\n")


def example_batch_translation():
    """示例3: 批量识别和翻译多张图片"""
    print("=" * 60)
    print("示例 3: 批量识别和翻译多张图片")
    print("=" * 60)
    
    # 检查 API 密钥
    if not os.getenv('ARK_API_KEY'):
        print("警告: 未设置 ARK_API_KEY 环境变量")
        print("跳过此示例\n")
        return
    
    # 初始化服务（启用翻译）
    service = TextRecognitionService(
        lang='japan',
        use_gpu=False,
        enable_translation=True,
        source_lang='ja',
        target_lang='zh'
    )
    
    # 准备图片列表
    image_paths = [
        "manga_page1.jpg",
        "manga_page2.jpg",
        "manga_page3.jpg"
    ]
    
    # 过滤存在的图片
    existing_images = [img for img in image_paths if os.path.exists(img)]
    
    if not existing_images:
        print("没有找到可用的图片文件")
        print("请将图片路径替换为实际存在的文件\n")
        return
    
    # 批量识别和翻译
    all_results = service.recognize_batch(existing_images, output_dir="output_translated/")
    
    # 汇总结果
    print(f"\n批量处理完成，共处理 {len(all_results)} 张图片")
    for image_path, results in all_results.items():
        translated_count = sum(1 for r in results if r.get('translation_success', False))
        print(f"  {image_path}: {len(results)} 条文本, {translated_count} 条翻译成功")
    
    print("\n")


def example_multilingual_translation():
    """示例4: 多语言识别和翻译"""
    print("=" * 60)
    print("示例 4: 多语言识别和翻译")
    print("=" * 60)
    
    if not os.getenv('ARK_API_KEY'):
        print("警告: 未设置 ARK_API_KEY 环境变量")
        print("跳过此示例\n")
        return
    
    # 英文翻译成中文
    print("\n1. 识别英文并翻译成中文:")
    service_en = TextRecognitionService(
        lang='en',
        enable_translation=True,
        source_lang='en',
        target_lang='zh'
    )
    
    english_image = "english_text.jpg"
    if os.path.exists(english_image):
        results = service_en.recognize_text(english_image, output_file="output_en_zh.txt")
        print(f"处理完成，识别 {len(results)} 条文本")
    else:
        print(f"英文图片不存在: {english_image}")
    
    # 日文翻译成英文
    print("\n2. 识别日文并翻译成英文:")
    service_ja = TextRecognitionService(
        lang='japan',
        enable_translation=True,
        source_lang='ja',
        target_lang='en'
    )
    
    japanese_image = "manga.jpg"
    if os.path.exists(japanese_image):
        results = service_ja.recognize_text(japanese_image, output_file="output_ja_en.txt")
        print(f"处理完成，识别 {len(results)} 条文本")
    else:
        print(f"日文图片不存在: {japanese_image}")
    
    print("\n")


def example_custom_processing_with_translation():
    """示例5: 自定义处理识别和翻译结果"""
    print("=" * 60)
    print("示例 5: 自定义处理识别和翻译结果")
    print("=" * 60)
    
    if not os.getenv('ARK_API_KEY'):
        print("警告: 未设置 ARK_API_KEY 环境变量")
        print("跳过此示例\n")
        return
    
    service = TextRecognitionService(
        lang='japan',
        enable_translation=True,
        source_lang='ja',
        target_lang='zh'
    )
    
    image_path = "manga.jpg"
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        print("请将 'manga.jpg' 替换为实际的图片路径\n")
        return
    
    # 识别并翻译（不保存到文件）
    results = service.recognize_text(image_path)
    
    # 自定义处理：只提取翻译成功的文本
    successful_translations = [
        r for r in results if r.get('translation_success', False)
    ]
    
    print(f"\n翻译成功的文本共 {len(successful_translations)} 条:")
    for i, result in enumerate(successful_translations, 1):
        print(f"{i}. {result['text']} → {result['translated']}")
    
    # 自定义处理：生成双语对照文本
    bilingual_text = []
    for result in results:
        if 'translated' in result and result.get('translation_success', False):
            bilingual_text.append(f"{result['text']} / {result['translated']}")
        else:
            bilingual_text.append(result['text'])
    
    full_bilingual = "\n".join(bilingual_text)
    print(f"\n双语对照文本:\n{full_bilingual}")
    
    # 保存自定义格式
    with open("custom_bilingual_output.txt", "w", encoding="utf-8") as f:
        f.write("=== 双语对照文本 ===\n\n")
        for i, result in enumerate(results, 1):
            f.write(f"{i}. 原文: {result['text']}\n")
            if 'translated' in result and result.get('translation_success', False):
                f.write(f"   译文: {result['translated']}\n")
            else:
                f.write(f"   译文: [翻译失败]\n")
            f.write(f"   置信度: {result['confidence']:.4f}\n\n")
    
    print("\n自定义双语结果已保存到 custom_bilingual_output.txt\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("PaddleOCR 文本识别与翻译服务 - 使用示例")
    print("=" * 60 + "\n")
    
    print("提示：")
    print("1. 请先准备好测试图片，并修改示例代码中的图片路径")
    print("2. 如需使用翻译功能，请先设置环境变量:")
    print("   export ARK_API_KEY='your-api-key-here'")
    print("3. 取消下面相应示例函数的注释来运行\n")
    
    # 运行示例（实际使用时取消注释）
    # example_single_image()
    # example_ocr_with_translation()
    # example_batch_translation()
    # example_multilingual_translation()
    # example_custom_processing_with_translation()
    
    print("=" * 60)
    print("示例演示完成")
    print("=" * 60)
    print("\n使用说明：")
    print("1. 编辑此文件，将图片路径替换为实际的文件路径")
    print("2. 设置 ARK_API_KEY 环境变量（如需翻译）")
    print("3. 取消相应示例函数的注释")
    print("4. 运行: python3 examples/api_example.py")
    print("\n")


if __name__ == '__main__':
    main()
