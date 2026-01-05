#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 文本识别服务
基于 PaddleOCR 实现图片中的文本识别功能，并支持 ARK 翻译和图片处理
"""

import os
import sys
import argparse
from datetime import datetime
from paddleocr import PaddleOCR
from translation_service import TranslationService
from image_processing_service import ImageProcessingService
import numpy as np


class TextRecognitionService:
    """文本识别服务类 - 使用 PP-OCRv5_server 模型"""
    
    def __init__(self, lang='japan', use_angle_cls=True, use_gpu=False, 
                 enable_translation=False, source_lang='ja', target_lang='zh',
                 ark_api_key=None, ark_model=None, enable_image_processing=False,
                 font_path=None, font_size=20, use_enhanced_detection=False,
                 det_db_thresh=0.3, det_db_box_thresh=0.5, det_db_unclip_ratio=1.6,
                 det_limit_side_len=None, det_limit_type='min', det_max_side_len=None,
                 enable_char_correction=False, correction_confidence_threshold=0.7,
                 custom_correction_rules=None):
        """
        初始化 PaddleOCR PP-OCRv5_server、翻译服务和图片处理服务
        
        Args:
            lang: 语言类型，默认为日文 'japan'，也支持 'ch', 'en' 等
            use_angle_cls: 是否使用方向分类器
            use_gpu: 是否使用GPU加速
            enable_translation: 是否启用翻译功能
            source_lang: 源语言代码（用于翻译）
            target_lang: 目标语言代码（用于翻译）
            ark_api_key: ARK API 密钥
            ark_model: ARK 模型端点
            enable_image_processing: 是否启用图片处理（inpaint + 绘制翻译文本）
            font_path: 字体文件路径（用于绘制翻译文本）
            font_size: 默认字体大小
            use_enhanced_detection: 是否使用增强检测参数（提高漫画识别准确率）
            det_db_thresh: 检测阈值（默认0.3，降低可检测更多文本）
            det_db_box_thresh: 文本框阈值（默认0.5，降低可减少漏检）
            det_db_unclip_ratio: 扩大检测框（默认1.6，增大可减少漏字）
            det_limit_side_len: 图片边长限制，None则不限制
            det_limit_type: 限制类型 'min' 或 'max'
            det_max_side_len: 最大边长限制
            enable_char_correction: 是否启用字符纠错（修正形近字误判）
            correction_confidence_threshold: 纠错置信度阈值
            custom_correction_rules: 自定义纠错规则字典
        """
        # 标准化语言参数 - PaddleOCR 使用 'japan' 而不是 'ja'
        lang_map = {
            'ja': 'japan',
            'japanese': 'japan',
            'japan': 'japan',
            'china': 'ch',
            'chinese': 'ch',
            'ch': 'ch',
            'en': 'en',
            'english': 'en'
        }
        ocr_lang = lang_map.get(lang.lower(), lang)
        
        # 初始化 PaddleOCR with PP-OCRv5_server 模型
        ocr_params = {
            'lang': ocr_lang,
            'use_angle_cls': use_angle_cls,
            'use_gpu': use_gpu,
            'show_log': False,
            'det_model_dir': None,  # 使用 PP-OCRv5_server_det
            'rec_model_dir': None,  # 使用 PP-OCRv5_server_rec
        }
        
        # 如果启用增强检测，添加检测参数
        if use_enhanced_detection:
            ocr_params.update({
                'det_db_thresh': det_db_thresh,
                'det_db_box_thresh': det_db_box_thresh,
                'det_db_unclip_ratio': det_db_unclip_ratio
            })
            
            # 添加边长限制参数（如果提供）
            if det_limit_side_len is not None:
                ocr_params['det_limit_side_len'] = det_limit_side_len
                ocr_params['det_limit_type'] = det_limit_type
            
            if det_max_side_len is not None:
                ocr_params['det_max_side_len'] = det_max_side_len
            
            print(f"启用增强检测参数: thresh={det_db_thresh}, box_thresh={det_db_box_thresh}, unclip_ratio={det_db_unclip_ratio}")
            if det_limit_side_len:
                print(f"  边长限制: {det_limit_type}={det_limit_side_len}, max={det_max_side_len}")
        
        try:
            self.ocr = PaddleOCR(**ocr_params)
            print(f"PaddleOCR PP-OCRv5_server 初始化成功 (语言: {ocr_lang}, GPU: {use_gpu})")
        except Exception as e:
            print(f"警告: 使用默认参数初始化 PaddleOCR: {str(e)}")
            # 回退到基础配置
            self.ocr = PaddleOCR(
                lang=ocr_lang,
                use_angle_cls=use_angle_cls,
                use_gpu=use_gpu,
                show_log=False
            )
            print(f"PaddleOCR 初始化成功（默认配置）")
        
        self.use_enhanced_detection = use_enhanced_detection
        
        # 初始化字符纠错服务
        self.enable_char_correction = enable_char_correction
        self.char_corrector = None
        if enable_char_correction:
            try:
                from character_correction_service import CharacterCorrectionService
                self.char_corrector = CharacterCorrectionService(
                    confidence_threshold=correction_confidence_threshold,
                    custom_rules=custom_correction_rules
                )
                print(f"字符纠错功能已启用 (阈值: {correction_confidence_threshold})")
            except Exception as e:
                print(f"警告: 字符纠错服务初始化失败: {str(e)}")
                self.enable_char_correction = False
        
        # 初始化翻译服务
        self.enable_translation = enable_translation
        self.translation_service = None
        if enable_translation:
            try:
                self.translation_service = TranslationService(
                    api_key=ark_api_key,
                    model=ark_model
                )
                self.source_lang = TranslationService.get_language_code(source_lang)
                self.target_lang = TranslationService.get_language_code(target_lang)
                print(f"翻译功能已启用 ({self.source_lang} -> {self.target_lang})")
            except Exception as e:
                print(f"警告: 翻译服务初始化失败: {str(e)}")
                print("将继续执行，但不进行翻译")
                self.enable_translation = False
        
        # 初始化图片处理服务
        self.enable_image_processing = enable_image_processing
        self.image_processor = None
        if enable_image_processing:
            try:
                self.image_processor = ImageProcessingService(
                    font_path=font_path,
                    font_size=font_size
                )
                print(f"图片处理功能已启用")
            except Exception as e:
                print(f"警告: 图片处理服务初始化失败: {str(e)}")
                print("将继续执行，但不进行图片处理")
                self.enable_image_processing = False
    
    def merge_text_boxes(self, text_boxes, distance_threshold=30, reading_order='rtl'):
        """
        合并相邻的文本框，解决文本被拆分成多段的问题
        使用基于距离的智能合并算法
        
        Args:
            text_boxes: OCR识别的文本框列表
            distance_threshold: 距离阈值（像素），距离小于此值的文本框会被合并
            reading_order: 阅读顺序 'rtl'(从右到左，日文漫画) 或 'ltr'(从左到右)
        
        Returns:
            合并后的文本框列表
        """
        if not text_boxes:
            return []
        
        if len(text_boxes) == 1:
            return text_boxes
        
        # 使用并查集进行基于距离的文本框分组
        n = len(text_boxes)
        parent = list(range(n))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # 计算两个文本框之间的距离
        def box_distance(box1, box2):
            # 获取文本框的中心点和边界
            def get_bbox(box):
                x_coords = [p[0] for p in box['position']]
                y_coords = [p[1] for p in box['position']]
                return {
                    'x_min': min(x_coords),
                    'x_max': max(x_coords),
                    'y_min': min(y_coords),
                    'y_max': max(y_coords),
                    'x_center': sum(x_coords) / 4,
                    'y_center': sum(y_coords) / 4
                }
            
            bbox1 = get_bbox(box1)
            bbox2 = get_bbox(box2)
            
            # 计算两个框之间的最短距离
            # 如果两个框重叠或相邻，返回较小的距离
            x_dist = 0
            if bbox1['x_max'] < bbox2['x_min']:
                x_dist = bbox2['x_min'] - bbox1['x_max']
            elif bbox2['x_max'] < bbox1['x_min']:
                x_dist = bbox1['x_min'] - bbox2['x_max']
            
            y_dist = 0
            if bbox1['y_max'] < bbox2['y_min']:
                y_dist = bbox2['y_min'] - bbox1['y_max']
            elif bbox2['y_max'] < bbox1['y_min']:
                y_dist = bbox1['y_min'] - bbox2['y_max']
            
            # 使用欧氏距离
            return (x_dist**2 + y_dist**2)**0.5
        
        # 根据距离合并文本框
        for i in range(n):
            for j in range(i + 1, n):
                dist = box_distance(text_boxes[i], text_boxes[j])
                if dist < distance_threshold:
                    union(i, j)
        
        # 将属于同一组的文本框归类
        groups = {}
        for i in range(n):
            root = find(i)
            if root not in groups:
                groups[root] = []
            groups[root].append(text_boxes[i])
        
        # 合并每个组内的文本框
        merged = []
        for group_boxes in groups.values():
            merged_box = self._merge_group_texts(group_boxes, reading_order)
            merged.append(merged_box)
        
        # 根据阅读顺序排序最终结果
        if reading_order == 'rtl':
            # 日文漫画：从右到左，从上到下
            merged.sort(key=lambda x: (-x['position'][0][0], x['position'][0][1]))
        else:
            # 从左到右，从上到下
            merged.sort(key=lambda x: (x['position'][0][0], x['position'][0][1]))
        
        return merged
    
    def _merge_group_texts(self, group_boxes, reading_order='rtl'):
        """
        合并同一组内的文本框
        
        Args:
            group_boxes: 同一组内的文本框列表
            reading_order: 阅读顺序
        
        Returns:
            合并后的单个文本框
        """
        if not group_boxes:
            return None
        
        if len(group_boxes) == 1:
            return group_boxes[0].copy()
        
        # 根据阅读顺序排序组内的文本框
        if reading_order == 'rtl':
            # 日文：从右到左，从上到下
            sorted_boxes = sorted(group_boxes, key=lambda x: (-x['position'][0][0], x['position'][0][1]))
        else:
            # 从左到右，从上到下
            sorted_boxes = sorted(group_boxes, key=lambda x: (x['position'][0][0], x['position'][0][1]))
        
        # 合并文本和计算平均置信度
        merged_text = ''.join([box['text'] for box in sorted_boxes])
        avg_confidence = sum([box['confidence'] for box in sorted_boxes]) / len(sorted_boxes)
        
        # 计算合并后的位置框（包含所有框的最小外接矩形）
        all_points = []
        for box in sorted_boxes:
            all_points.extend(box['position'])
        
        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]
        
        merged_position = [
            [min(x_coords), min(y_coords)],  # 左上
            [max(x_coords), min(y_coords)],  # 右上
            [max(x_coords), max(y_coords)],  # 右下
            [min(x_coords), max(y_coords)]   # 左下
        ]
        
        return {
            'text': merged_text,
            'confidence': avg_confidence,
            'position': merged_position
        }
    
    def recognize_text(self, image_path, output_file=None, output_image=None, merge_boxes=False, 
                       merge_distance=30, reading_order='rtl'):
        """
        识别图片中的文本，并可选翻译和生成处理后的图片
        
        Args:
            image_path: 图片路径
            output_file: 输出文本文件路径（可选）
            output_image: 输出处理后的图片路径（可选）
            merge_boxes: 是否合并相邻的文本框（解决文本分段问题）
            merge_distance: 合并距离阈值（像素），距离小于此值的文本框会被合并
            reading_order: 阅读顺序 'rtl'(从右到左，日文漫画) 或 'ltr'(从左到右)
        
        Returns:
            识别结果列表
        """
        # 检查图片是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        print(f"\n正在识别图片: {image_path}")
        
        # 使用 PaddleOCR 进行文本识别（包含检测和识别）
        print("正在进行文本检测和识别...")
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or len(result) == 0 or not result[0]:
            print("未检测到文本")
            return []
        
        # 解析OCR结果
        recognized_texts = []
        for line in result[0]:
            position = line[0]  # 四边形坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_info = line[1]  # (text, confidence)
            text = text_info[0]
            confidence = text_info[1]
            
            recognized_texts.append({
                'text': text,
                'confidence': confidence,
                'position': position
            })
        
        print(f"成功识别 {len(recognized_texts)} 个文本")
        
        # 字符纠错（如果启用）
        if self.enable_char_correction and self.char_corrector:
            print("正在进行字符纠错...")
            recognized_texts = self.char_corrector.correct_batch(recognized_texts)
        
        # 如果启用文本框合并，进行合并处理
        if merge_boxes:
            original_count = len(recognized_texts)
            recognized_texts = self.merge_text_boxes(
                recognized_texts, 
                distance_threshold=merge_distance,
                reading_order=reading_order
            )
            print(f"文本框合并: {original_count} 个 → {len(recognized_texts)} 个 (距离阈值: {merge_distance}px, 阅读顺序: {'从右到左' if reading_order == 'rtl' else '从左到右'})")
        
        # 输出识别结果
        print("\n" + "="*60)
        print("识别结果:")
        print("="*60)
        for idx, item in enumerate(recognized_texts):
            print(f"{idx + 1}. {item['text']} (置信度: {item['confidence']:.4f})")
        print("="*60)
        
        # 翻译识别到的文本
        if self.enable_translation and self.translation_service:
            print("\n" + "="*60)
            print("翻译结果:")
            print("="*60)
            
            texts_to_translate = [item['text'] for item in recognized_texts]
            translations = self.translation_service.translate_batch(
                texts_to_translate,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                show_progress=True
            )
            
            # 将翻译结果添加到识别结果中
            for idx, (item, trans_result) in enumerate(zip(recognized_texts, translations)):
                item['translated'] = trans_result['translated']
                item['translation_success'] = trans_result['success']
                
                # 输出翻译结果到控制台
                if trans_result['success']:
                    print(f"{idx + 1}. {trans_result['translated']}")
                else:
                    print(f"{idx + 1}. [翻译失败] {item['text']}")
            
            print("="*60)
        
        # 如果启用图片处理且有翻译结果，生成处理后的图片
        if self.enable_image_processing and self.image_processor and self.enable_translation:
            if output_image:
                output_image_path = output_image
            else:
                # 自动生成输出图片路径
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_dir = os.path.dirname(image_path) or '.'
                output_image_path = os.path.join(output_dir, f"{base_name}_translated.jpg")
            
            try:
                self.image_processor.process_image_with_translation(
                    image_path,
                    recognized_texts,
                    output_image_path,
                    inpaint=True,
                    draw_translated=True
                )
            except Exception as e:
                print(f"警告: 图片处理失败: {str(e)}")
        
        # 如果指定了输出文件，则保存结果
        if output_file:
            self._save_to_file(image_path, recognized_texts, output_file)
        
        return recognized_texts
    
    def _save_to_file(self, image_path, recognized_texts, output_file):
        """
        将识别结果保存到文件
        
        Args:
            image_path: 源图片路径
            recognized_texts: 识别结果列表
            output_file: 输出文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"图片路径: {image_path}\n")
            f.write(f"识别时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"识别文本数量: {len(recognized_texts)}\n")
            f.write(f"翻译状态: {'已启用' if self.enable_translation else '未启用'}\n")
            f.write("\n" + "="*60 + "\n")
            f.write("识别结果:\n")
            f.write("="*60 + "\n\n")
            
            for idx, item in enumerate(recognized_texts):
                f.write(f"{idx + 1}. 原文: {item['text']}\n")
                f.write(f"   置信度: {item['confidence']:.4f}\n")
                f.write(f"   位置: {item['position']}\n")
                
                # 如果有翻译结果，也写入文件
                if 'translated' in item:
                    if item.get('translation_success', False):
                        f.write(f"   译文: {item['translated']}\n")
                    else:
                        f.write(f"   译文: [翻译失败]\n")
                
                f.write("\n")
        
        print(f"\n识别结果已保存到: {output_file}")
    
    def recognize_batch(self, image_paths, output_dir=None):
        """
        批量识别多张图片
        
        Args:
            image_paths: 图片路径列表
            output_dir: 输出目录（可选）
        
        Returns:
            所有识别结果的字典
        """
        all_results = {}
        
        for image_path in image_paths:
            output_file = None
            output_image = None
            
            if output_dir:
                # 为每张图片生成对应的输出文件名
                basename = os.path.basename(image_path)
                name_without_ext = os.path.splitext(basename)[0]
                output_file = os.path.join(output_dir, f"{name_without_ext}_ocr.txt")
                
                # 如果启用图片处理，也生成输出图片路径
                if self.enable_image_processing:
                    output_image = os.path.join(output_dir, f"{name_without_ext}_translated.jpg")
            
            try:
                results = self.recognize_text(image_path, output_file, output_image)
                all_results[image_path] = results
            except Exception as e:
                print(f"处理图片 {image_path} 时出错: {str(e)}")
                all_results[image_path] = []
        
        return all_results


def main():
    """命令行主入口"""
    parser = argparse.ArgumentParser(
        description='PaddleOCR 文本识别、翻译与图片处理服务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 识别单张图片
  python ocr_service.py -i image.jpg
  
  # 识别图片并保存结果到文件
  python ocr_service.py -i image.jpg -o result.txt
  
  # 识别并翻译（需要设置 ARK_API_KEY 环境变量）
  python ocr_service.py -i manga.jpg --translate --source-lang ja --target-lang zh
  
  # 识别、翻译并生成处理后的图片（inpaint + 绘制翻译文本）
  python ocr_service.py -i manga.jpg --translate --source-lang ja --target-lang zh --process-image --output-image result.jpg
  
  # 批量处理（识别、翻译、生成图片）
  python ocr_service.py -i img1.jpg img2.jpg img3.jpg --translate --process-image -o output/
  
  # 使用英文识别
  python ocr_service.py -i image.jpg --lang en
  
  # 使用GPU加速
  python ocr_service.py -i image.jpg --gpu
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        nargs='+',
        required=True,
        help='输入图片路径（支持多个图片）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件/目录路径（单图片时为文件，多图片时为目录）'
    )
    
    parser.add_argument(
        '--output-image',
        help='输出处理后的图片路径（仅单图片时有效，需配合 --process-image）'
    )
    
    parser.add_argument(
        '--lang',
        default='ch',
        choices=['ch', 'en', 'korean', 'japan', 'chinese_cht', 'ta', 'te', 'ka', 'latin', 'arabic', 'cyrillic', 'devanagari'],
        help='识别语言类型，默认为中文 (ch)'
    )
    
    parser.add_argument(
        '--gpu',
        action='store_true',
        help='使用GPU加速（需要安装GPU版本的PaddlePaddle）'
    )
    
    # 翻译相关参数
    parser.add_argument(
        '--translate',
        action='store_true',
        help='启用翻译功能（需要设置 ARK_API_KEY 环境变量）'
    )
    
    parser.add_argument(
        '--source-lang',
        default='ja',
        help='源语言代码，默认为日语 (ja)。支持: zh, en, ja, ko 等'
    )
    
    parser.add_argument(
        '--target-lang',
        default='zh',
        help='目标语言代码，默认为中文 (zh)。支持: zh, en, ja, ko 等'
    )
    
    parser.add_argument(
        '--ark-api-key',
        help='ARK API 密钥（也可通过环境变量 ARK_API_KEY 设置）'
    )
    
    parser.add_argument(
        '--ark-model',
        help=f'ARK 模型端点（可选，默认: {TranslationService.DEFAULT_MODEL}）'
    )
    
    # 图片处理相关参数
    parser.add_argument(
        '--process-image',
        action='store_true',
        help='启用图片处理功能（inpaint 原文本区域并绘制翻译文本，需配合 --translate 使用）'
    )
    
    parser.add_argument(
        '--font-path',
        help='字体文件路径（用于绘制翻译文本，可选）'
    )
    
    parser.add_argument(
        '--font-size',
        type=int,
        default=20,
        help='默认字体大小（默认: 20）'
    )
    
    args = parser.parse_args()
    
    # 初始化服务
    try:
        service = TextRecognitionService(
            lang=args.lang,
            use_angle_cls=True,
            use_gpu=args.gpu,
            enable_translation=args.translate,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            ark_api_key=args.ark_api_key,
            ark_model=args.ark_model,
            enable_image_processing=args.process_image,
            font_path=args.font_path,
            font_size=args.font_size
        )
    except Exception as e:
        print(f"初始化服务失败: {str(e)}")
        print("请确保已正确安装依赖并配置 API 密钥")
        sys.exit(1)
    
    # 处理输入
    image_paths = args.input
    
    if len(image_paths) == 1:
        # 单张图片
        try:
            service.recognize_text(
                image_paths[0], 
                output_file=args.output,
                output_image=args.output_image
            )
        except Exception as e:
            print(f"识别失败: {str(e)}")
            sys.exit(1)
    else:
        # 多张图片
        output_dir = args.output if args.output else 'output'
        try:
            service.recognize_batch(image_paths, output_dir)
            print(f"\n批量处理完成，共处理 {len(image_paths)} 张图片")
        except Exception as e:
            print(f"批量处理失败: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
