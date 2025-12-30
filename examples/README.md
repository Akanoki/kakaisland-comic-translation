# 示例文件说明

本目录包含 PaddleOCR 文本识别服务的使用示例。

## 文件列表

### api_example.py

演示如何使用 Python API 调用文本识别服务，包含以下示例：

1. **单张图片识别** - 基本的单图片识别功能
2. **批量图片识别** - 同时处理多张图片
3. **多语言识别** - 识别不同语言的文本
4. **自定义处理** - 对识别结果进行自定义处理

### 使用方法

1. 准备测试图片，放在项目目录或指定路径
2. 编辑 `api_example.py`，将图片路径替换为实际路径
3. 取消相应示例函数的注释
4. 运行示例：

```bash
cd /path/to/kakaisland-comic-translation
python3 examples/api_example.py
```

## 命令行示例

### 基础示例

```bash
# 识别单张图片
python3 ocr_service.py -i examples/test_image.jpg

# 识别并保存结果
python3 ocr_service.py -i examples/test_image.jpg -o output/result.txt
```

### 批量处理示例

```bash
# 批量识别目录中的所有 JPG 图片
python3 ocr_service.py -i images/*.jpg -o output/

# 批量识别指定的多张图片
python3 ocr_service.py -i img1.jpg img2.jpg img3.jpg -o output/
```

### 多语言示例

```bash
# 识别英文
python3 ocr_service.py -i english_doc.jpg --lang en -o result_en.txt

# 识别日文
python3 ocr_service.py -i manga_page.jpg --lang japan -o result_jp.txt

# 识别繁体中文
python3 ocr_service.py -i traditional_chinese.jpg --lang chinese_cht -o result_cht.txt
```

### GPU 加速示例

```bash
# 使用 GPU 加速处理大图片
python3 ocr_service.py -i large_image.jpg --gpu -o result.txt
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

## 输出结果示例

识别结果文件示例（`result.txt`）：

```
图片路径: test_image.jpg
识别时间: 2024-01-01 12:00:00
识别文本数量: 3

============================================================
识别结果:
============================================================

1. 欢迎使用PaddleOCR
   置信度: 0.9856
   位置: [[10, 20], [200, 20], [200, 50], [10, 50]]

2. 文本识别服务
   置信度: 0.9723
   位置: [[10, 60], [180, 60], [180, 90], [10, 90]]

3. 高精度识别
   置信度: 0.9645
   位置: [[10, 100], [150, 100], [150, 130], [10, 130]]
```

## 常见使用场景

### 场景 1: 漫画翻译

```bash
# 识别漫画页面中的文字
python3 ocr_service.py -i manga_page.jpg --lang japan -o translations/page1.txt
```

### 场景 2: 文档数字化

```bash
# 批量识别扫描的文档
python3 ocr_service.py -i scans/*.jpg -o digitized/
```

### 场景 3: 图片文字提取

```bash
# 从截图中提取文字
python3 ocr_service.py -i screenshot.png -o extracted_text.txt
```

## 更多帮助

查看完整的使用文档，请参考项目根目录的 [README.md](../README.md)
