#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARK 翻译服务
基于火山引擎 ARK API 实现文本翻译功能
"""

import os
import requests
import json
from typing import List, Dict, Optional


class TranslationService:
    """翻译服务类"""
    
    # 默认配置
    DEFAULT_MODEL = "ep-20251229173446-nv2rg"
    DEFAULT_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, api_url: Optional[str] = None):
        """
        初始化翻译服务
        
        Args:
            api_key: ARK API 密钥，如果未提供则从环境变量 ARK_API_KEY 读取
            model: 使用的模型端点，默认使用 DEFAULT_MODEL
            api_url: API 端点 URL，默认使用 DEFAULT_API_URL
        """
        self.api_key = api_key or os.getenv('ARK_API_KEY')
        if not self.api_key:
            raise ValueError("未提供 ARK API 密钥。请设置环境变量 ARK_API_KEY 或通过参数传入")
        
        self.model = model or self.DEFAULT_MODEL
        self.api_url = api_url or self.DEFAULT_API_URL
        print(f"翻译服务初始化成功 (模型: {self.model})")
    
    def translate_text(
        self, 
        text: str, 
        source_lang: str = "zh", 
        target_lang: str = "en"
    ) -> Optional[str]:
        """
        翻译单条文本
        
        Args:
            text: 待翻译的文本
            source_lang: 源语言代码 (如: zh, en, ja, ko)
            target_lang: 目标语言代码 (如: zh, en, ja, ko)
        
        Returns:
            翻译后的文本，失败时返回 None
        """
        if not text or not text.strip():
            return ""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # ARK API 使用类似 OpenAI Chat Completion 格式的请求结构
        # 支持通过 translation_options 指定翻译参数
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text,
                            "translation_options": {
                                "source_language": source_lang,
                                "target_language": target_lang
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # 提取翻译结果
                if 'choices' in result and len(result['choices']) > 0:
                    translated = result['choices'][0].get('message', {}).get('content', '')
                    return translated
                else:
                    print(f"警告: API 响应格式异常: {result}")
                    return None
            else:
                print(f"翻译失败 (HTTP {response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"翻译超时: {text[:50]}...")
            return None
        except requests.exceptions.RequestException as e:
            print(f"翻译请求失败: {str(e)}")
            return None
        except Exception as e:
            print(f"翻译过程出错: {str(e)}")
            return None
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "zh",
        target_lang: str = "en",
        show_progress: bool = True
    ) -> List[Dict[str, str]]:
        """
        批量翻译文本
        
        Args:
            texts: 待翻译的文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            show_progress: 是否显示进度
        
        Returns:
            包含原文和译文的字典列表
        """
        results = []
        total = len(texts)
        
        for idx, text in enumerate(texts, 1):
            if show_progress:
                print(f"翻译进度: {idx}/{total}")
            
            translated = self.translate_text(text, source_lang, target_lang)
            
            results.append({
                'original': text,
                'translated': translated if translated else "",
                'success': translated is not None
            })
        
        return results
    
    @staticmethod
    def get_language_code(lang: str) -> str:
        """
        将常见语言名称转换为语言代码
        
        Args:
            lang: 语言名称或代码
        
        Returns:
            标准语言代码
        """
        lang_map = {
            'ch': 'zh',
            'chinese': 'zh',
            'china': 'zh',
            'zh': 'zh',
            'en': 'en',
            'english': 'en',
            'ja': 'ja',
            'japan': 'ja',
            'japanese': 'ja',
            'ko': 'ko',
            'korean': 'ko',
            'korea': 'ko',
        }
        
        return lang_map.get(lang.lower(), lang.lower())
