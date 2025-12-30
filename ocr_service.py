#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 文本识别服务
基于 PaddleOCR 实现图片中的文本识别功能，并支持 ARK 翻译
"""

import os
import sys
import argparse
from datetime import datetime
from paddleocr import PaddleOCR
from translation_service import TranslationService


class TextRecognitionService:
    """文本识别服务类"""
    
    def __init__(self, lang='japan', use_angle_cls=True, use_gpu=False, 
                 enable_translation=False, source_lang='ja', target_lang='zh',
                 ark_api_key=None, ark_model=None):
        """
        初始化 PaddleOCR 和翻译服务
        
        Args:
            lang: 语言类型，默认为日文 'japan'，也支持 'ch', 'en' 等
            use_angle_cls: 是否使用方向分类器
            use_gpu: 是否使用GPU加速
            enable_translation: 是否启用翻译功能
            source_lang: 源语言代码（用于翻译）
            target_lang: 目标语言代码（用于翻译）
            ark_api_key: ARK API 密钥
            ark_model: ARK 模型端点
        """
        self.ocr = PaddleOCR(
            lang=lang,
            use_angle_cls=use_angle_cls,
            use_gpu=use_gpu,
            show_log=False
        )
        print(f"PaddleOCR 初始化成功 (语言: {lang}, GPU: {use_gpu})")
        
        # 初始化翻译服务
        self.enable_translation = enable_translation
        self.translation_service = None
        if enable_translation:
            try:
                self.translation_service = TranslationService(
                    api_key=ark_api_key,
                    model=ark_model or "ep-20251229173446-nv2rg"
                )
                self.source_lang = TranslationService.get_language_code(source_lang)
                self.target_lang = TranslationService.get_language_code(target_lang)
                print(f"翻译功能已启用 ({self.source_lang} -> {self.target_lang})")
            except Exception as e:
                print(f"警告: 翻译服务初始化失败: {str(e)}")
                print("将继续执行，但不进行翻译")
                self.enable_translation = False
    
    def recognize_text(self, image_path, output_file=None):
        """
        识别图片中的文本，并可选翻译
        
        Args:
            image_path: 图片路径
            output_file: 输出文件路径（可选）
        
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
        print("\n" + "="*60)
        print("识别结果:")
        print("="*60)
        
        for idx, line in enumerate(result[0]):
            # line[0] 是坐标框, line[1] 是 (文本, 置信度)
            text = line[1][0]
            confidence = line[1][1]
            recognized_texts.append({
                'text': text,
                'confidence': confidence,
                'position': line[0]
            })
            
            # 输出到控制台
            print(f"{idx + 1}. {text} (置信度: {confidence:.4f})")
        
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
            if output_dir:
                # 为每张图片生成对应的输出文件名
                basename = os.path.basename(image_path)
                name_without_ext = os.path.splitext(basename)[0]
                output_file = os.path.join(output_dir, f"{name_without_ext}_ocr.txt")
            
            try:
                results = self.recognize_text(image_path, output_file)
                all_results[image_path] = results
            except Exception as e:
                print(f"处理图片 {image_path} 时出错: {str(e)}")
                all_results[image_path] = []
        
        return all_results


def main():
    """命令行主入口"""
    parser = argparse.ArgumentParser(
        description='PaddleOCR 文本识别与翻译服务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 识别单张图片
  python ocr_service.py -i image.jpg
  
  # 识别图片并保存结果到文件
  python ocr_service.py -i image.jpg -o result.txt
  
  # 识别并翻译（需要设置 ARK_API_KEY 环境变量）
  python ocr_service.py -i manga.jpg --translate --source-lang ja --target-lang zh
  
  # 批量识别多张图片
  python ocr_service.py -i img1.jpg img2.jpg img3.jpg -o output/
  
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
        default='ep-20251229173446-nv2rg',
        help='ARK 模型端点，默认为 ep-20251229173446-nv2rg'
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
            ark_model=args.ark_model
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
            service.recognize_text(image_paths[0], args.output)
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
