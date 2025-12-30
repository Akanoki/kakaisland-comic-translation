#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片处理服务
使用 OpenCV 进行文本区域的修复（inpaint）和翻译文本的绘制
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import os


class ImageProcessingService:
    """图片处理服务类"""
    
    def __init__(self, font_path: Optional[str] = None, font_size: int = 20):
        """
        初始化图片处理服务
        
        Args:
            font_path: 字体文件路径（可选，用于绘制翻译文本）
            font_size: 默认字体大小
        """
        self.font_path = font_path
        self.font_size = font_size
        print(f"图片处理服务初始化成功 (字体大小: {font_size})")
    
    def create_mask_from_boxes(self, image_shape: Tuple[int, int], boxes: List[List]) -> np.ndarray:
        """
        根据文本框位置创建遮罩
        
        Args:
            image_shape: 图片形状 (height, width)
            boxes: 文本框位置列表，每个元素为 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        
        Returns:
            遮罩图像（用于 inpaint）
        """
        mask = np.zeros(image_shape[:2], dtype=np.uint8)
        
        for box in boxes:
            # 将浮点坐标转换为整数
            points = np.array(box, dtype=np.int32)
            # 填充多边形区域
            cv2.fillPoly(mask, [points], 255)
        
        # 稍微扩大遮罩区域，确保完全覆盖文本
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        return mask
    
    def inpaint_text_regions(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        使用 inpaint 算法修复文本区域
        
        Args:
            image: 原始图片
            mask: 文本区域遮罩
        
        Returns:
            修复后的图片
        """
        # 使用 Telea 算法进行修复
        inpainted = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        return inpainted
    
    def calculate_font_size(self, box: List[List], text_length: int) -> int:
        """
        根据文本框大小和文本长度计算合适的字体大小
        
        Args:
            box: 文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_length: 文本字符数量
        
        Returns:
            合适的字体大小
        """
        # 计算文本框的宽度和高度
        points = np.array(box, dtype=np.float32)
        width = np.linalg.norm(points[1] - points[0])
        height = np.linalg.norm(points[3] - points[0])
        
        # 根据文本长度和框大小计算字体大小
        if text_length > 0:
            # 预估每个字符占用的宽度
            char_width = width / text_length
            font_size = int(min(char_width * 1.2, height * 0.8))
            # 限制字体大小范围
            font_size = max(10, min(font_size, 50))
        else:
            font_size = self.font_size
        
        return font_size
    
    def draw_text_on_image(
        self, 
        image: np.ndarray, 
        text: str, 
        box: List[List],
        font_size: Optional[int] = None,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        bg_color: Optional[Tuple[int, int, int]] = None
    ) -> np.ndarray:
        """
        在图片上绘制文本
        
        Args:
            image: 图片（numpy 数组）
            text: 要绘制的文本
            box: 文本框位置 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            font_size: 字体大小（可选，自动计算）
            text_color: 文本颜色 (B, G, R)
            bg_color: 背景颜色（可选）
        
        Returns:
            绘制文本后的图片
        """
        # 转换为 PIL Image 以支持中文字体
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        
        # 计算文本框的中心点和大小
        points = np.array(box, dtype=np.float32)
        center_x = int(np.mean(points[:, 0]))
        center_y = int(np.mean(points[:, 1]))
        
        # 自动计算字体大小
        if font_size is None:
            font_size = self.calculate_font_size(box, len(text))
        
        # 尝试加载字体
        try:
            if self.font_path and os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                # 尝试使用系统默认中文字体
                font = self._get_default_font(font_size)
        except Exception as e:
            print(f"警告: 加载字体失败 ({str(e)})，使用默认字体")
            font = ImageFont.load_default()
        
        # 获取文本边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算文本绘制位置（居中）
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        
        # 如果指定了背景颜色，先绘制背景
        if bg_color is not None:
            padding = 5
            bg_box = [
                text_x - padding,
                text_y - padding,
                text_x + text_width + padding,
                text_y + text_height + padding
            ]
            draw.rectangle(bg_box, fill=bg_color)
        
        # 绘制文本（PIL 使用 RGB 顺序）
        text_color_rgb = (text_color[2], text_color[1], text_color[0])
        draw.text((text_x, text_y), text, font=font, fill=text_color_rgb)
        
        # 转换回 OpenCV 格式
        result = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        return result
    
    def _get_default_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        获取默认中文字体
        
        Args:
            size: 字体大小
        
        Returns:
            字体对象
        """
        # 常见的中文字体路径
        font_paths = [
            # Linux
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Windows
            "C:\\Windows\\Fonts\\msyh.ttc",  # 微软雅黑
            "C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
        
        # 如果都失败，返回默认字体
        return ImageFont.load_default()
    
    def process_image_with_translation(
        self,
        image_path: str,
        ocr_results: List[Dict],
        output_path: str,
        inpaint: bool = True,
        draw_translated: bool = True
    ) -> str:
        """
        处理图片：修复原文本区域并绘制翻译文本
        
        Args:
            image_path: 原始图片路径
            ocr_results: OCR 识别结果列表，包含 position, text, translated 等字段
            output_path: 输出图片路径
            inpaint: 是否进行 inpaint 修复
            draw_translated: 是否绘制翻译文本
        
        Returns:
            输出图片路径
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        processed_image = image.copy()
        
        # 如果需要 inpaint，先修复原文本区域
        if inpaint and ocr_results:
            boxes = [result['position'] for result in ocr_results]
            mask = self.create_mask_from_boxes(image.shape, boxes)
            processed_image = self.inpaint_text_regions(processed_image, mask)
            print(f"已修复 {len(boxes)} 个文本区域")
        
        # 如果需要绘制翻译文本
        if draw_translated:
            translated_count = 0
            for result in ocr_results:
                if 'translated' in result and result.get('translation_success', False):
                    translated_text = result['translated']
                    if translated_text:
                        processed_image = self.draw_text_on_image(
                            processed_image,
                            translated_text,
                            result['position'],
                            text_color=(0, 0, 0),  # 黑色文本
                            bg_color=(255, 255, 255)  # 白色背景
                        )
                        translated_count += 1
            
            print(f"已绘制 {translated_count} 条翻译文本")
        
        # 保存处理后的图片
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        cv2.imwrite(output_path, processed_image)
        print(f"处理后的图片已保存到: {output_path}")
        
        return output_path
