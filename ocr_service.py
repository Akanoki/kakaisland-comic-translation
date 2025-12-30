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


class TextRecognitionService:
    """文本识别服务类"""
    
    def __init__(self, lang='japan', use_angle_cls=True, use_gpu=False, 
                 enable_translation=False, source_lang='ja', target_lang='zh',
                 ark_api_key=None, ark_model=None, enable_image_processing=False,
                 font_path=None, font_size=20, use_enhanced_detection=False,
                 det_db_thresh=0.3, det_db_box_thresh=0.5, det_db_unclip_ratio=1.6):
        """
        初始化 PaddleOCR、翻译服务和图片处理服务
        
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
        """
        # 根据是否使用增强检测设置参数
        ocr_params = {
            'lang': lang,
            'use_angle_cls': use_angle_cls,
            'use_gpu': use_gpu,
            'show_log': False
        }
        
        if use_enhanced_detection:
            ocr_params.update({
                'det_db_thresh': det_db_thresh,
                'det_db_box_thresh': det_db_box_thresh,
                'det_db_unclip_ratio': det_db_unclip_ratio
            })
            print(f"启用增强检测参数: thresh={det_db_thresh}, box_thresh={det_db_box_thresh}, unclip_ratio={det_db_unclip_ratio}")
        
        self.ocr = PaddleOCR(**ocr_params)
        self.use_enhanced_detection = use_enhanced_detection
        print(f"PaddleOCR 初始化成功 (语言: {lang}, GPU: {use_gpu})")
        
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
    
    def merge_text_boxes(self, text_boxes, vertical_threshold=20, horizontal_threshold=50):
        """
        合并相邻的文本框，解决文本被拆分成多段的问题
        
        Args:
            text_boxes: OCR识别的文本框列表
            vertical_threshold: 垂直方向阈值（像素），小于此值的文本框会被合并
            horizontal_threshold: 水平方向阈值（像素），用于判断是否在同一列
        
        Returns:
            合并后的文本框列表
        """
        if not text_boxes:
            return []
        
        # 按位置排序：先按x坐标（列），再按y坐标（行）
        sorted_boxes = sorted(text_boxes, key=lambda x: (x['position'][0][0], x['position'][0][1]))
        
        merged = []
        current_column = [sorted_boxes[0]]
        
        for box in sorted_boxes[1:]:
            # 获取当前列最后一个框和新框的位置
            last_box = current_column[-1]
            last_x = last_box['position'][0][0]
            last_y_bottom = max(p[1] for p in last_box['position'])
            
            current_x = box['position'][0][0]
            current_y_top = min(p[1] for p in box['position'])
            
            # 判断是否在同一列
            x_diff = abs(current_x - last_x)
            y_diff = current_y_top - last_y_bottom
            
            if x_diff < horizontal_threshold and y_diff < vertical_threshold:
                # 在同一列且垂直距离很近，加入当前列
                current_column.append(box)
            else:
                # 新列或距离太远，合并当前列并开始新列
                merged.extend(self._merge_column_texts(current_column))
                current_column = [box]
        
        # 合并最后一列
        merged.extend(self._merge_column_texts(current_column))
        
        return merged
    
    def _merge_column_texts(self, column_boxes):
        """
        合并同一列内的文本框
        
        Args:
            column_boxes: 同一列内的文本框列表
        
        Returns:
            合并后的文本框列表（如果很接近则合并为一个）
        """
        if not column_boxes:
            return []
        
        if len(column_boxes) == 1:
            return column_boxes
        
        # 按y坐标排序（从上到下）
        sorted_column = sorted(column_boxes, key=lambda x: x['position'][0][1])
        
        merged = []
        current = sorted_column[0].copy()
        
        for box in sorted_column[1:]:
            current_bottom = max(p[1] for p in current['position'])
            next_top = min(p[1] for p in box['position'])
            
            # 垂直距离很近，合并文本
            if next_top - current_bottom < 15:
                current['text'] += box['text']
                current['confidence'] = (current['confidence'] + box['confidence']) / 2
                # 扩展位置框（保持左上角，扩展右下角）
                current['position'] = [
                    current['position'][0],  # 左上
                    current['position'][1],  # 右上
                    box['position'][2],      # 右下
                    box['position'][3]       # 左下
                ]
            else:
                merged.append(current)
                current = box.copy()
        
        merged.append(current)
        return merged
    
    def recognize_text(self, image_path, output_file=None, output_image=None, merge_boxes=False):
        """
        识别图片中的文本，并可选翻译和生成处理后的图片
        
        Args:
            image_path: 图片路径
            output_file: 输出文本文件路径（可选）
            output_image: 输出处理后的图片路径（可选）
            merge_boxes: 是否合并相邻的文本框（解决文本分段问题）
        
        Returns:
            识别结果列表
        """
        # 检查图片是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        print(f"\n正在识别图片: {image_path}")
        
        # 执行OCR识别
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            print("未检测到文本内容")
            return []
        
        # 提取识别结果
        recognized_texts = []
        for idx, line in enumerate(result[0]):
            # line[0] 是坐标框, line[1] 是 (文本, 置信度)
            text = line[1][0]
            confidence = line[1][1]
            recognized_texts.append({
                'text': text,
                'confidence': confidence,
                'position': line[0]
            })
        
        # 如果启用文本框合并，进行合并处理
        if merge_boxes:
            original_count = len(recognized_texts)
            recognized_texts = self.merge_text_boxes(recognized_texts)
            print(f"文本框合并: {original_count} 个 → {len(recognized_texts)} 个")
        
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
