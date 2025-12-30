# kakaisland-comic-translation
漫画翻译 / Manga Translation

基于 PaddleOCR 实现的文本识别服务，用于识别图片中的文本内容。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装配置](#安装配置)
  - [1. 安装 Python](#1-安装-python)
  - [2. 安装 PaddlePaddle](#2-安装-paddlepaddle)
  - [3. 安装 PaddleOCR 和其他依赖](#3-安装-paddleocr-和其他依赖)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
  - [命令行方式](#命令行方式)
  - [Python API 方式](#python-api-方式)
- [配置说明](#配置说明)
- [示例](#示例)
- [常见问题](#常见问题)
- [参考文档](#参考文档)

## 功能特性

- ✅ 支持中文、英文等多种语言的文本识别
- ✅ 识别结果同时输出到控制台和文件
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

## 快速开始

### 1. 准备测试图片

将需要识别的图片放在项目目录下，或者使用绝对路径。

### 2. 运行识别

```bash
# 识别单张图片（输出到控制台）
python3 ocr_service.py -i your_image.jpg

# 识别图片并保存结果到文件
python3 ocr_service.py -i your_image.jpg -o result.txt
```

### 3. 查看结果

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

# 初始化服务
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

### 示例 3：批量识别多语言

```bash
# 识别英文图片
python3 ocr_service.py -i english_doc.jpg --lang en -o result_en.txt

# 识别日文图片
python3 ocr_service.py -i japanese_manga.jpg --lang japan -o result_jp.txt
```

### 示例 4：批量处理

```bash
python3 ocr_service.py -i page1.jpg page2.jpg page3.jpg -o output/
```

### 示例 5：使用 GPU 加速

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

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请在 [GitHub Issues](https://github.com/Akanoki/kakaisland-comic-translation/issues) 中提出。
