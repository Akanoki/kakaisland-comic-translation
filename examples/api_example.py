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
    
    image_path = "your_manga.jpg"  # 替换为你的图片路径
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


def example_enhanced_manga_recognition():
    """示例7: 增强型漫画识别（优化参数 + 文本合并）- 提高准确率"""
    print("=" * 60)
    print("示例 7: 增强型漫画识别 - 解决漏字和文本拆分问题")
    print("=" * 60)
    
    # ========================================
    # 配置区域 - 在此处直接设置参数
    # ========================================
    
    # ARK API 密钥
    ARK_API_KEY = "6ecd7934-fd45-4484-8f40-42a2ae4c94db"  # 替换为你的实际 API 密钥
    
    # 图片路径
    image_path = "C:\\Users\\ADMIN\\Desktop\\kakaisland\\01_111.jpg"  # 替换为你的漫画图片路径
    
    # 输出路径
    output_text_file = "manga_enhanced_result.txt"
    output_image_file = "manga_enhanced_translated.jpg"
    
    # 语言设置
    ocr_lang = 'japan'      # 日文漫画
    source_lang = 'ja'
    target_lang = 'zh'
    
    # ========================================
    # 增强检测参数 - 提高识别准确率
    # ========================================
    use_enhanced_detection = True    # 启用增强检测
    det_db_thresh = 0.2              # 检测阈值（降低以检测更多文本，默认0.3）
    det_db_box_thresh = 0.4          # 文本框阈值（降低以减少漏检，默认0.6）
    det_db_unclip_ratio = 2.0        # 扩大检测框（增大以减少漏字，默认1.5）
    
    merge_boxes = True               # 启用文本框合并（解决拆分问题）
    merge_distance = 50              # 合并距离阈值（像素），距离小于此值的文本框会被合并
    reading_order = 'rtl'            # 阅读顺序：'rtl'=从右到左（日文漫画），'ltr'=从左到右
    
    # ========================================
    # 执行处理
    # ========================================
    
    print(f"\n配置信息:")
    print(f"  图片路径: {image_path}")
    print(f"  OCR 语言: {ocr_lang}")
    print(f"  增强检测: {'启用' if use_enhanced_detection else '禁用'}")
    if use_enhanced_detection:
        print(f"    - det_db_thresh: {det_db_thresh} (降低可检测更多文本)")
        print(f"    - det_db_box_thresh: {det_db_box_thresh} (降低可减少漏检)")
        print(f"    - det_db_unclip_ratio: {det_db_unclip_ratio} (增大可减少漏字)")
    print(f"  文本框合并: {'启用' if merge_boxes else '禁用'}")
    if merge_boxes:
        print(f"    - 合并距离: {merge_distance}px (距离小于此值的文本框会合并)")
        print(f"    - 阅读顺序: {'从右到左（日文漫画）' if reading_order == 'rtl' else '从左到右'}")
    print(f"  翻译: {source_lang} → {target_lang}\n")
    
    # 检查图片
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        print("请修改 image_path 变量\n")
        return
    
    # 检查 API 密钥
    if ARK_API_KEY == "your-api-key-here":
        print("警告: 请先设置 ARK_API_KEY\n")
        return
    
    try:
        # 初始化增强型服务
        print("正在初始化增强型 OCR 服务...")
        service = TextRecognitionService(
            lang=ocr_lang,
            use_angle_cls=True,              # 启用方向分类器
            use_gpu=False,                    # 根据硬件情况设置
            enable_translation=True,
            source_lang=source_lang,
            target_lang=target_lang,
            ark_api_key=ARK_API_KEY,
            enable_image_processing=True,
            # 增强检测参数
            use_enhanced_detection=use_enhanced_detection,
            det_db_thresh=det_db_thresh,
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio
        )
        
        # 执行识别、翻译和图片处理
        print("\n开始处理...")
        results = service.recognize_text(
            image_path,
            output_file=output_text_file,
            output_image=output_image_file,
            merge_boxes=merge_boxes,         # 启用文本框合并
            merge_distance=merge_distance,   # 合并距离阈值
            reading_order=reading_order      # 阅读顺序
        )
        
        # 显示结果摘要
        print("\n" + "=" * 60)
        print("处理完成！增强功能说明：")
        print("=" * 60)
        print(f"\n✓ 使用增强检测参数，减少漏字问题")
        print(f"✓ 启用文本框合并，解决句子拆分问题")
        print(f"✓ 共处理 {len(results)} 条文本")
        
        # 显示部分结果
        if results:
            print(f"\n前 3 条结果:")
            for i in range(min(3, len(results))):
                result = results[i]
                print(f"\n{i + 1}. 原文: {result['text']}")
                if 'translated' in result and result.get('translation_success', False):
                    print(f"   译文: {result['translated']}")
        
        print(f"\n输出文件:")
        print(f"  文本: {output_text_file}")
        print(f"  图片: {output_image_file}")
        
        print("\n" + "=" * 60)
        print("参数调优建议：")
        print("=" * 60)
        print("检测参数调优：")
        print("• 如果还有漏字：进一步降低 det_db_thresh (0.2 → 0.15)")
        print("• 如果检测太多噪点：提高 det_db_box_thresh (0.4 → 0.5)")
        print("• 如果字被截断：增大 det_db_unclip_ratio (2.0 → 2.5)")
        print("\n文本合并调优：")
        print("• 如果合并太多（不该合的合了）：降低 merge_distance (50 → 30)")
        print("• 如果合并太少（该合的没合）：增大 merge_distance (50 → 80)")
        print("• 阅读顺序错误：检查 reading_order 参数")
        print("  - 日文漫画用 'rtl' (从右到左)")
        print("  - 中英文用 'ltr' (从左到右)")
        print("\n")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print("请检查配置和依赖安装\n")


def example_complete_workflow_with_api_key():
    """示例6: 完整工作流（设置 API 密钥、识别、翻译、生成图片）- 推荐使用"""
    print("=" * 60)
    print("示例 6: 完整工作流 - 识别、翻译、生成处理后的图片")
    print("=" * 60)
    
    # ========================================
    # 配置区域 - 在此处直接设置参数
    # ========================================
    
    # ARK API 密钥 - 直接在这里设置，无需环境变量
    ARK_API_KEY = "6ecd7934-fd45-4484-8f40-42a2ae4c94db"  # 替换为你的实际 API 密钥
    
    # 图片路径
    image_path = "C:\\Users\\ADMIN\\Desktop\\kakaisland\\01_111.jpg"  # 替换为你的图片路径
    
    # 输出路径
    output_text_file = "output_result.txt"  # 文本结果输出路径
    output_image_file = "manga_translated.jpg"  # 处理后的图片输出路径
    
    # 语言设置
    ocr_lang = 'japan'      # OCR 识别语言：'ch'(中文), 'en'(英文), 'japan'(日文), 'korean'(韩文)
    source_lang = 'ja'      # 翻译源语言：'zh'(中文), 'en'(英文), 'ja'(日文), 'ko'(韩文)
    target_lang = 'zh'      # 翻译目标语言：'zh'(中文), 'en'(英文), 'ja'(日文), 'ko'(韩文)
    
    # 字体设置（可选）
    font_path = None        # 自定义字体路径，None 则使用系统默认字体
    font_size = 20          # 字体大小
    
    # ========================================
    # 执行处理
    # ========================================
    
    print(f"\n配置信息:")
    print(f"  图片路径: {image_path}")
    print(f"  OCR 语言: {ocr_lang}")
    print(f"  翻译: {source_lang} → {target_lang}")
    print(f"  输出文本: {output_text_file}")
    print(f"  输出图片: {output_image_file}\n")
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        print("请修改上面的 image_path 变量，指向实际的图片路径\n")
        return
    
    # 检查 API 密钥
    if ARK_API_KEY == "your-api-key-here":
        print("警告: 请先设置 ARK_API_KEY 变量为你的实际 API 密钥")
        print("修改上面的 ARK_API_KEY = 'your-api-key-here' 这一行\n")
        return
    
    try:
        # 初始化服务
        print("正在初始化服务...")
        service = TextRecognitionService(
            lang=ocr_lang,
            use_gpu=False,
            enable_translation=True,        # 启用翻译
            source_lang=source_lang,
            target_lang=target_lang,
            ark_api_key=ARK_API_KEY,        # 直接传入 API 密钥
            enable_image_processing=True,   # 启用图片处理
            font_path=font_path,
            font_size=font_size
        )
        
        # 执行识别、翻译和图片处理
        print("\n开始处理...")
        results = service.recognize_text(
            image_path,
            output_file=output_text_file,
            output_image=output_image_file
        )
        
        # 显示结果摘要
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"\n共处理 {len(results)} 条文本")
        
        # 显示前几条结果
        max_display = min(3, len(results))
        if max_display > 0:
            print(f"\n前 {max_display} 条结果预览:")
            for i in range(max_display):
                result = results[i]
                print(f"\n{i + 1}. 原文: {result['text']}")
                if 'translated' in result and result.get('translation_success', False):
                    print(f"   译文: {result['translated']}")
                print(f"   置信度: {result['confidence']:.4f}")
        
        print(f"\n输出文件:")
        print(f"  文本结果: {output_text_file}")
        print(f"  处理后图片: {output_image_file}")
        print("\n处理成功！请查看输出文件。\n")
        
    except Exception as e:
        print(f"\n错误: 处理失败")
        print(f"错误信息: {str(e)}")
        print("\n请检查:")
        print("1. ARK_API_KEY 是否正确")
        print("2. 图片路径是否正确")
        print("3. 是否已安装所有依赖 (pip install -r requirements.txt)")
        print("\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("PaddleOCR 文本识别与翻译服务 - 使用示例")
    print("=" * 60 + "\n")
    
    print("🌟 推荐使用示例 7 - 增强型漫画识别（解决漏字和拆分问题）")
    print("=" * 60)
    print("示例 7 专门针对漫画优化，提供:")
    print("  ✓ 增强检测参数，减少漏字")
    print("  ✓ 文本框智能合并，解决句子拆分")
    print("  ✓ 直接设置 API 密钥，无需环境变量")
    print("  ✓ 完整 OCR → 翻译 → 图片生成 工作流\n")
    
    print("其他示例说明:")
    print("1. 示例 1: 基础 OCR 识别（不翻译）")
    print("2. 示例 2: OCR + 翻译")
    print("3. 示例 3: 批量处理")
    print("4. 示例 4: 多语言翻译")
    print("5. 示例 5: 自定义处理")
    print("6. 示例 6: 完整工作流")
    print("7. 示例 7: 增强型漫画识别（最新推荐）⭐⭐⭐\n")
    
    print("快速开始（针对漫画识别）：")
    print("1. 编辑 example_enhanced_manga_recognition() 函数")
    print("2. 设置 ARK_API_KEY、image_path 等参数")
    print("3. 根据需要调整检测参数（det_db_thresh, det_db_box_thresh, det_db_unclip_ratio）")
    print("4. 取消下面 example_enhanced_manga_recognition() 的注释")
    print("5. 运行: python3 examples/api_example.py\n")
    
    # 运行示例（实际使用时取消注释）
    # example_single_image()
    # example_ocr_with_translation()
    # example_batch_translation()
    # example_multilingual_translation()
    # example_custom_processing_with_translation()
    # example_complete_workflow_with_api_key()
    
    # 最新推荐 - 增强型漫画识别
    example_enhanced_manga_recognition()
    
    print("=" * 60)
    print("使用说明")
    print("=" * 60)
    print("请取消上面相应示例函数的注释来运行")
    print("推荐使用 example_enhanced_manga_recognition() 获得最佳漫画识别效果\n")


if __name__ == '__main__':
    main()
