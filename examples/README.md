# 示例文件说明

本目录包含 PaddleOCR 文本识别与翻译服务的使用示例。

## 文件列表

### api_example.py

演示如何使用 Python API 调用文本识别和翻译服务，包含以下示例：

1. **单张图片识别（不翻译）** - 基本的单图片识别功能
2. **识别日文图片并翻译成中文** - OCR + 翻译的完整流程
3. **批量识别和翻译多张图片** - 同时处理多张图片并翻译
4. **多语言识别和翻译** - 支持多种语言对的翻译
5. **自定义处理识别和翻译结果** - 对识别和翻译结果进行自定义处理
6. **完整工作流示例（推荐）** ⭐ - 直接设置 API 密钥，完整的识别、翻译、图片处理流程

### 快速开始 - 推荐方式

**示例 6** 是最简单的使用方式，无需设置环境变量：

1. 编辑 `api_example.py` 中的 `example_complete_workflow_with_api_key()` 函数
2. 在配置区域设置参数：
   ```python
   ARK_API_KEY = "your-actual-api-key"  # 直接设置 API 密钥
   image_path = "your-image.jpg"        # 设置图片路径
   ```
3. 取消函数调用的注释
4. 运行：
   ```bash
   cd /path/to/kakaisland-comic-translation
   python3 examples/api_example.py
   ```

这个示例会：
- ✅ 识别图片中的文本
- ✅ 翻译识别的文本
- ✅ 生成处理后的图片（移除原文本，绘制翻译文本）
- ✅ 保存文本结果到文件

### 传统使用方法（需要环境变量）

1. 准备测试图片，放在项目目录或指定路径
2. 设置 ARK API 密钥（如需翻译功能）：
   ```bash
   export ARK_API_KEY='your-api-key-here'
   ```
3. 编辑 `api_example.py`，将图片路径替换为实际路径
4. 取消相应示例函数的注释
5. 运行示例：

```bash
cd /path/to/kakaisland-comic-translation
python3 examples/api_example.py
```

## 命令行示例

### 基础示例（仅识别）

```bash
# 识别单张图片
python3 ocr_service.py -i examples/test_image.jpg

# 识别并保存结果
python3 ocr_service.py -i examples/test_image.jpg -o output/result.txt
```

### 识别+翻译示例

```bash
# 设置 API 密钥
export ARK_API_KEY='your-api-key-here'

# 识别日文漫画并翻译成中文
python3 ocr_service.py -i manga_page.jpg --lang japan --translate --source-lang ja --target-lang zh -o result.txt

# 识别英文并翻译成中文
python3 ocr_service.py -i english_doc.jpg --lang en --translate --source-lang en --target-lang zh -o result.txt
```

### 批量处理示例

```bash
# 批量识别目录中的所有 JPG 图片
python3 ocr_service.py -i images/*.jpg -o output/

# 批量识别和翻译多张漫画页
python3 ocr_service.py -i page1.jpg page2.jpg page3.jpg --lang japan --translate --source-lang ja --target-lang zh -o output/
```

### 多语言示例

```bash
# 识别日文
python3 ocr_service.py -i manga_page.jpg --lang japan -o result_jp.txt

# 识别繁体中文
python3 ocr_service.py -i traditional_chinese.jpg --lang chinese_cht -o result_cht.txt

# 识别韩文并翻译成中文
python3 ocr_service.py -i korean_text.jpg --lang korean --translate --source-lang ko --target-lang zh -o result.txt
```

### GPU 加速示例

```bash
# 使用 GPU 加速处理大图片
python3 ocr_service.py -i large_image.jpg --gpu -o result.txt

# GPU 加速 + 翻译
python3 ocr_service.py -i large_manga.jpg --gpu --lang japan --translate --source-lang ja --target-lang zh -o result.txt
```

## 准备测试图片

你可以：

1. 使用自己的图片（漫画、文档、截图等）
2. 从网络下载测试图片
3. 使用手机拍摄包含文字的照片

**注意事项：**
- 图片格式支持：JPG, PNG, BMP 等常见格式
- 建议图片清晰度足够，文字可读
- 过大的图片会增加处理时间，建议长边不超过 2000 像素
- 翻译功能需要设置 ARK_API_KEY 环境变量

## 输出结果示例

### 仅识别的结果文件示例（`result.txt`）：

```
图片路径: test_image.jpg
识别时间: 2024-01-01 12:00:00
识别文本数量: 3
翻译状态: 未启用

============================================================
识别结果:
============================================================

1. 原文: 欢迎使用PaddleOCR
   置信度: 0.9856
   位置: [[10, 20], [200, 20], [200, 50], [10, 50]]

2. 原文: 文本识别服务
   置信度: 0.9723
   位置: [[10, 60], [180, 60], [180, 90], [10, 90]]
```

### 识别+翻译的结果文件示例（`translated.txt`）：

```
图片路径: manga.jpg
识别时间: 2024-01-01 12:00:00
识别文本数量: 2
翻译状态: 已启用

============================================================
识别结果:
============================================================

1. 原文: こんにちは
   置信度: 0.9856
   位置: [[10, 20], [200, 20], [200, 50], [10, 50]]
   译文: 你好

2. 原文: ありがとう
   置信度: 0.9723
   位置: [[10, 60], [180, 60], [180, 90], [10, 90]]
   译文: 谢谢
```

## 常见使用场景

### 场景 1: 漫画翻译（识别+翻译）

```bash
# 设置 API 密钥
export ARK_API_KEY='your-api-key-here'

# 识别日文漫画并翻译成中文
python3 ocr_service.py -i manga_page.jpg --lang japan --translate --source-lang ja --target-lang zh -o translations/page1.txt
```

### 场景 2: 文档数字化（仅识别）

```bash
# 批量识别扫描的文档
python3 ocr_service.py -i scans/*.jpg -o digitized/
```

### 场景 3: 图片文字提取并翻译

```bash
# 从英文截图中提取文字并翻译成中文
python3 ocr_service.py -i screenshot.png --lang en --translate --source-lang en --target-lang zh -o extracted_translated.txt
```

## 更多帮助

查看完整的使用文档，请参考项目根目录的 [README.md](../README.md)
