#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 文本识别服务
基于 PaddleOCR 实现图片中的文本识别功能
"""

import os
import sys
import argparse
from datetime import datetime
from paddleocr import PaddleOCR
import cv2


class TextRecognitionService:
    """文本识别服务类"""
    
    def __init__(self, lang='ch', use_angle_cls=True, use_gpu=False):
        """
        初始化 PaddleOCR
        
        Args:
            lang: 语言类型，默认为中文 'ch'，也支持 'en' 等
            use_angle_cls: 是否使用方向分类器
            use_gpu: 是否使用GPU加速
        """
        self.ocr = PaddleOCR(
            lang=lang,
            use_angle_cls=use_angle_cls,
            use_gpu=use_gpu,
            show_log=False
        )
        print(f"PaddleOCR 初始化成功 (语言: {lang}, GPU: {use_gpu})")
    
    def recognize_text(self, image_path, output_file=None):
        """
        识别图片中的文本
        
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
            f.write("\n" + "="*60 + "\n")
            f.write("识别结果:\n")
            f.write("="*60 + "\n\n")
            
            for idx, item in enumerate(recognized_texts):
                f.write(f"{idx + 1}. {item['text']}\n")
                f.write(f"   置信度: {item['confidence']:.4f}\n")
                f.write(f"   位置: {item['position']}\n\n")
        
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
        description='PaddleOCR 文本识别服务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 识别单张图片
  python ocr_service.py -i image.jpg
  
  # 识别图片并保存结果到文件
  python ocr_service.py -i image.jpg -o result.txt
  
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
    
    args = parser.parse_args()
    
    # 初始化服务
    try:
        service = TextRecognitionService(
            lang=args.lang,
            use_angle_cls=True,
            use_gpu=args.gpu
        )
    except Exception as e:
        print(f"初始化 PaddleOCR 失败: {str(e)}")
        print("请确保已正确安装 PaddleOCR 和相关依赖")
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
