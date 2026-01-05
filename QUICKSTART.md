# 快速开始指南

本指南帮助您在 5 分钟内完成环境配置并运行第一个文本识别和翻译任务。

## 第一步：安装 Python

确保已安装 Python 3.7+：

```bash
python3 --version
```

如未安装，从 [python.org](https://www.python.org/downloads/) 下载。

## 第二步：克隆项目

```bash
git clone https://github.com/Akanoki/kakaisland-comic-translation.git
cd kakaisland-comic-translation
```

## 第三步：安装依赖

### CPU 版本（推荐）

```bash
# 安装 PaddlePaddle CPU 版
pip3 install paddlepaddle -i https://mirror.baidu.com/pypi/simple

# 安装项目依赖
pip3 install -r requirements.txt
```

### GPU 版本（可选，需要 NVIDIA 显卡）

```bash
# 安装 PaddlePaddle GPU 版（CUDA 11.2）
pip3 install paddlepaddle-gpu==2.5.0.post112 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# 安装项目依赖
pip3 install -r requirements.txt
```

## 第四步：配置 ARK API 密钥（可选，仅翻译功能需要）

如果需要使用翻译功能，设置环境变量：

```bash
# Linux/Mac
export ARK_API_KEY="your-api-key-here"

# Windows
set ARK_API_KEY=your-api-key-here
```

## 第五步：验证安装

```bash
python3 -c "from paddleocr import PaddleOCR; print('安装成功！')"
```

## 第六步：运行第一个识别任务

### 准备测试图片

将包含文字的图片（如截图、照片）放在项目目录下，例如 `test.jpg`

### 运行识别

```bash
# 基本识别（输出到控制台）
python3 ocr_service.py -i test.jpg

# 识别并保存结果
python3 ocr_service.py -i test.jpg -o result.txt
```

### 运行识别+翻译（需要配置 ARK API 密钥）

```bash
# 识别日文漫画并翻译成中文
python3 ocr_service.py -i manga.jpg --lang japan --translate --source-lang ja --target-lang zh -o result.txt
```

### 查看结果

- 控制台会显示识别的文本和翻译结果
- `result.txt` 包含详细的识别和翻译结果

## 常用命令

```bash
# 识别中文图片
python3 ocr_service.py -i chinese.jpg

# 识别英文图片
python3 ocr_service.py -i english.jpg --lang en

# 识别日文并翻译成中文
python3 ocr_service.py -i japanese.jpg --lang japan --translate --source-lang ja --target-lang zh

# 批量识别
python3 ocr_service.py -i img1.jpg img2.jpg img3.jpg -o output/

# 使用 GPU 加速
python3 ocr_service.py -i large.jpg --gpu
```

## 输出示例

```
PaddleOCR 初始化成功 (语言: ch, GPU: False)

正在识别图片: test.jpg

============================================================
识别结果:
============================================================
1. 欢迎使用 PaddleOCR (置信度: 0.9856)
2. 文本识别服务 (置信度: 0.9723)
============================================================

识别结果已保存到: result.txt
```

## 遇到问题？

### 问题 1：ModuleNotFoundError: No module named 'paddleocr'

**解决：**
```bash
pip3 install paddleocr
```

### 问题 2：识别不准确

**解决：**
- 确保图片清晰
- 使用正确的语言参数（`--lang`）
- 尝试调整图片大小

### 问题 3：安装很慢

**解决：**
使用国内镜像源：
```bash
pip3 install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

## 下一步

- 阅读完整文档：[README.md](README.md)
- 查看 API 示例：[examples/api_example.py](examples/api_example.py)
- 了解更多功能：[examples/README.md](examples/README.md)

## 获取帮助

- 查看帮助信息：`python3 ocr_service.py --help`
- 提交问题：[GitHub Issues](https://github.com/Akanoki/kakaisland-comic-translation/issues)

---

**恭喜！** 你已经完成了基本配置，可以开始使用 PaddleOCR 进行文本识别了！
