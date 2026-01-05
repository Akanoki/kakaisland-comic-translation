import json
from paddleocr import PaddleOCR
from ocr_service_1 import OCRService

def numpy_friendly(obj):
    if hasattr(obj, 'tolist'):
        return obj.tolist()
    # 对于无法序列化的对象，直接转为字符串
    return str(obj)

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)
image = "C:\\Users\\ADMIN\\Desktop\\kakaisland\\01_111.jpg"
results = ocr.predict(image)

result = results[0]

result_json_str = json.dumps(result, ensure_ascii=False, default=numpy_friendly)

ocr_service = OCRService()
text_regions = ocr_service.detect_and_recognize(
    paddleocr_json_str=result_json_str
)
print(text_regions)
