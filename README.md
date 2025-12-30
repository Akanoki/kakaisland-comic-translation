# kakaisland-comic-translation
漫画翻译 / Manga Translation

基于 PaddleOCR 实现的文本识别服务，集成 ARK 翻译 API，用于识别和翻译图片中的文本内容。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装配置](#安装配置)
  - [1. 安装 Python](#1-安装-python)
  - [2. 安装 PaddlePaddle](#2-安装-paddlepaddle)
  - [3. 安装 PaddleOCR 和其他依赖](#3-安装-paddleocr-和其他依赖)
  - [4. 配置 ARK API 密钥](#4-配置-ark-api-密钥)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
  - [命令行方式](#命令行方式)
  - [Python API 方式](#python-api-方式)
- [配置说明](#配置说明)
- [示例](#示例)
- [常见问题](#常见问题)
- [参考文档](#参考文档)

## 功能特性

- ✅ 支持中文、英文、日文、韩文等多种语言的文本识别
- ✅ 集成 ARK 翻译 API，支持自动翻译识别文本
- ✅ 识别和翻译结果同时输出到控制台和文件
- ✅ 支持单张图片和批量图片处理
- ✅ 支持 CPU 和 GPU 加速
- ✅ 提供命令行和 API 两种调用方式
- ✅ 输出文本位置和置信度信息

## 环境要求

- Python >= 3.7
- 操作系统：Windows / Linux / macOS
- （可选）CUDA 10.2+ 和 cuDNN 7.6+（用于 GPU 加速）

## 安装配置

### 1. 安装 Python

确保系统已安装 Python 3.7 或更高版本：

```bash
python --version
# 或
python3 --version
```

如果未安装，请从 [Python 官网](https://www.python.org/downloads/) 下载安装。

### 2. 安装 PaddlePaddle

PaddlePaddle 是 PaddleOCR 的底层深度学习框架。根据你的硬件环境选择合适的版本：

#### CPU 版本（推荐新手）

```bash
# Linux/Mac
python3 -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple

# Windows
python -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

#### GPU 版本（推荐有 NVIDIA 显卡的用户）

**前提条件：** 已安装 CUDA 和 cuDNN

```bash
# CUDA 11.2
python3 -m pip install paddlepaddle-gpu==2.5.0.post112 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# CUDA 10.2
python3 -m pip install paddlepaddle-gpu==2.5.0.post102 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

**详细安装说明请参考：**
- [PaddlePaddle 官方安装文档（中文）](https://www.paddlepaddle.org.cn/install/quick)
- [PaddlePaddle Installation Guide (English)](https://www.paddlepaddle.org.cn/en/install/quick)

### 3. 安装 PaddleOCR 和其他依赖

克隆本项目并安装依赖：

```bash
# 克隆项目
git clone https://github.com/Akanoki/kakaisland-comic-translation.git
cd kakaisland-comic-translation

# 安装项目依赖
pip install -r requirements.txt
```

**验证安装：**

```bash
python3 -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功！')"
```

### 4. 配置 ARK API 密钥

如果需要使用翻译功能，需要配置火山引擎 ARK API 密钥：

#### 方法一：设置环境变量（推荐）

```bash
# Linux/Mac
export ARK_API_KEY="your-api-key-here"

# Windows (CMD)
set ARK_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:ARK_API_KEY="your-api-key-here"
```

#### 方法二：通过命令行参数传递

```bash
python3 ocr_service.py -i image.jpg --translate --ark-api-key "your-api-key-here"
```

**获取 API 密钥：**
请访问 [火山引擎 ARK 平台](https://ark.cn-beijing.volces.com/) 注册并获取 API 密钥。

## 快速开始

### 1. 准备测试图片

将需要识别的图片放在项目目录下，或者使用绝对路径。

### 2. 运行识别（不翻译）

```bash
# 识别单张图片（输出到控制台）
python3 ocr_service.py -i your_image.jpg

# 识别图片并保存结果到文件
python3 ocr_service.py -i your_image.jpg -o result.txt
```

### 3. 运行识别和翻译

```bash
# 识别日文漫画并翻译成中文
export ARK_API_KEY="your-api-key-here"
python3 ocr_service.py -i manga.jpg --translate --lang japan --source-lang ja --target-lang zh

# 或者一次性指定 API 密钥
python3 ocr_service.py -i manga.jpg --translate --lang japan --source-lang ja --target-lang zh --ark-api-key "your-api-key-here"
```

### 4. 查看结果

- 控制台会直接显示识别的文本内容
- 如果指定了 `-o` 参数，结果会保存到指定的文件中

## 使用方法

### 命令行方式

#### 基本用法

```bash
python3 ocr_service.py -i <图片路径> [选项]
```

#### 命令行参数

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `-i, --input` | 输入图片路径（支持多个） | 是 | - |
| `-o, --output` | 输出文件/目录路径 | 否 | - |
| `--lang` | 识别语言类型 | 否 | ch（中文） |
| `--gpu` | 使用 GPU 加速 | 否 | False |

#### 支持的语言

- `ch`: 中文简体
- `en`: 英文
- `chinese_cht`: 中文繁体
- `japan`: 日文
- `korean`: 韩文
- `latin`: 拉丁文
- `arabic`: 阿拉伯文
- `cyrillic`: 西里尔文
- `devanagari`: 梵文字母

更多语言支持请参考 [PaddleOCR 语言列表](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/multi_languages.md)。

### Python API 方式

在你的 Python 代码中使用：

```python
from ocr_service import TextRecognitionService

# 初始化服务（仅识别，不翻译）
service = TextRecognitionService(
    lang='ch',        # 语言类型
    use_gpu=False     # 是否使用GPU
)

# 识别单张图片
results = service.recognize_text('image.jpg', output_file='result.txt')

# 批量识别
image_list = ['img1.jpg', 'img2.jpg', 'img3.jpg']
all_results = service.recognize_batch(image_list, output_dir='output/')

# 访问识别结果
for result in results:
    print(f"文本: {result['text']}")
    print(f"置信度: {result['confidence']}")
    print(f"位置: {result['position']}")
```

**启用翻译功能：**

```python
import os
from ocr_service import TextRecognitionService

# 设置 API 密钥（如果未设置环境变量）
# os.environ['ARK_API_KEY'] = 'your-api-key-here'

# 初始化服务（启用翻译）
service = TextRecognitionService(
    lang='japan',              # OCR 识别语言
    use_gpu=False,
    enable_translation=True,   # 启用翻译
    source_lang='ja',          # 源语言（日文）
    target_lang='zh',          # 目标语言（中文）
    ark_api_key=None           # 可选，默认从环境变量读取
)

# 识别并翻译
results = service.recognize_text('manga.jpg', output_file='translated.txt')

# 访问识别和翻译结果
for result in results:
    print(f"原文: {result['text']}")
    if 'translated' in result:
        print(f"译文: {result['translated']}")
    print(f"置信度: {result['confidence']}")
```

## 配置说明

### GPU 加速

如果你的设备有 NVIDIA GPU 并且已安装 CUDA，可以使用 GPU 加速：

```bash
python3 ocr_service.py -i image.jpg --gpu
```

### 自定义输出目录

批量处理时，可以指定输出目录：

```bash
python3 ocr_service.py -i img1.jpg img2.jpg img3.jpg -o output/
```

程序会在 `output/` 目录下为每张图片生成对应的识别结果文件。

## 示例

### 示例 1：识别单张图片

```bash
python3 ocr_service.py -i examples/chinese_text.jpg
```

输出示例：
```
PaddleOCR 初始化成功 (语言: ch, GPU: False)

正在识别图片: examples/chinese_text.jpg

============================================================
识别结果:
============================================================
1. 欢迎使用PaddleOCR (置信度: 0.9856)
2. 文本识别服务 (置信度: 0.9723)
============================================================
```

### 示例 2：识别并保存结果

```bash
python3 ocr_service.py -i comic_page.jpg -o output/comic_result.txt
```

### 示例 3：识别日文漫画并翻译成中文

```bash
python3 ocr_service.py -i japanese_manga.jpg --lang japan --translate --source-lang ja --target-lang zh -o result.txt
```

输出示例：
```
PaddleOCR 初始化成功 (语言: japan, GPU: False)
翻译服务初始化成功 (模型: ep-20251229173446-nv2rg)
翻译功能已启用 (ja -> zh)

正在识别图片: japanese_manga.jpg

============================================================
识别结果:
============================================================
1. こんにちは (置信度: 0.9856)
2. ありがとう (置信度: 0.9723)
============================================================

============================================================
翻译结果:
============================================================
翻译进度: 1/2
翻译进度: 2/2
1. 你好
2. 谢谢
============================================================

识别结果已保存到: result.txt
```

### 示例 4：批量识别多语言

```bash
# 识别英文图片
python3 ocr_service.py -i english_doc.jpg --lang en -o result_en.txt

# 识别日文图片
python3 ocr_service.py -i japanese_manga.jpg --lang japan -o result_jp.txt
```

### 示例 5：批量处理

```bash
python3 ocr_service.py -i page1.jpg page2.jpg page3.jpg -o output/
```

### 示例 6：使用 GPU 加速

```bash
python3 ocr_service.py -i large_image.jpg --gpu -o result.txt
```

## 常见问题

### Q1: 提示 "ModuleNotFoundError: No module named 'paddleocr'"

**解决方法：**
```bash
pip install paddleocr
```

### Q2: 识别准确率不高

**解决方法：**
- 确保图片清晰度足够
- 尝试调整图片大小（建议长边不超过 2000 像素）
- 使用正确的语言参数（`--lang`）

### Q3: GPU 版本安装失败

**解决方法：**
- 检查 CUDA 版本是否匹配
- 参考 [PaddlePaddle 官方文档](https://www.paddlepaddle.org.cn/install/quick) 选择正确的版本
- 如遇问题，可先使用 CPU 版本

### Q4: 如何处理大量图片？

**解决方法：**
使用批量处理功能：
```bash
# 使用通配符
python3 ocr_service.py -i images/*.jpg -o output/

# 或者在 Python 脚本中循环处理
```

### Q5: 内存不足

**解决方法：**
- 分批处理图片
- 减小图片尺寸
- 使用 GPU 版本可以减少 CPU 内存占用

### Q6: 翻译功能无法使用

**解决方法：**
- 确保已设置 ARK_API_KEY 环境变量或通过 --ark-api-key 参数传递
- 检查 API 密钥是否有效
- 确认网络连接正常，可以访问火山引擎 ARK API
- 查看错误信息，根据提示进行排查

### Q7: 翻译结果不准确

**解决方法：**
- 确认源语言和目标语言设置正确（--source-lang 和 --target-lang）
- OCR 识别语言（--lang）应与源语言一致
- 检查 OCR 识别结果是否准确，翻译质量依赖于识别质量

## 参考文档

### PaddleOCR 官方文档
- **PaddleOCR GitHub**: https://github.com/PaddlePaddle/PaddleOCR
- **快速开始（中文）**: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/quickstart.md
- **多语言支持**: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/multi_languages.md
- **API 文档**: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/whl.md

### PaddlePaddle 官方文档
- **官方网站（中文）**: https://www.paddlepaddle.org.cn/
- **安装指南（中文）**: https://www.paddlepaddle.org.cn/install/quick
- **Installation Guide (English)**: https://www.paddlepaddle.org.cn/en/install/quick
- **GitHub**: https://github.com/PaddlePaddle/Paddle

### 其他资源
- **PaddleOCR 在线体验**: https://www.paddlepaddle.org.cn/hub/scene/ocr
- **模型库**: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md

### 火山引擎 ARK 翻译 API
- **ARK 平台**: https://ark.cn-beijing.volces.com/
- **API 文档**: https://www.volcengine.com/docs/82379/1263512

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请在 [GitHub Issues](https://github.com/Akanoki/kakaisland-comic-translation/issues) 中提出。
