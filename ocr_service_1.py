"""
OCR Service for parsing PaddleOCR JSON results + 竖排漫画文本框合并
"""
import logging
import json
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class OCRService:
    """OCR Service to parse PaddleOCR JSON results + merge adjacent boxes."""

    def __init__(self):
        pass

    # ---------------- 对外主入口 ----------------
    def detect_and_recognize(
            self,
            confidence_threshold: float = 0.6,
            paddleocr_json_str: Optional[str] = None,
            merge_boxes: bool = True,
            max_col_gap: int = 60,      # 列中心最大水平间距
            max_row_gap: int = 70,      # 行最大垂直空隙
            reading_order: str = "rtl"
    ) -> List[Dict[str, Any]]:
        """
        1. 解析 JSON -> 2. 过滤低置信度 -> 3. 合并相邻框
        """
        if not paddleocr_json_str:
            print("PaddleOCR JSON string is empty")
            logger.error("PaddleOCR JSON string is empty")
            return []

        try:
            ocr_result = json.loads(paddleocr_json_str)
            # pruned_result = ocr_result.get("ocrResults", [{}])[0].get("prunedResult", {})
            dt_polys = ocr_result.get("dt_polys", [])
            rec_texts = ocr_result.get("rec_texts", [])
            rec_scores = ocr_result.get("rec_scores", [])
            rec_boxes = ocr_result.get("rec_boxes", [])

            if not all(len(arr) == len(rec_texts) for arr in [dt_polys, rec_scores, rec_boxes]):
                logger.error("OCR result arrays have inconsistent lengths")
                return []

            # 先解析成统一格式
            text_regions = []
            for idx in range(len(rec_texts)):
                conf = rec_scores[idx]
                if conf < confidence_threshold:
                    continue
                text = rec_texts[idx].strip()
                if not text:
                    continue
                box = dt_polys[idx]
                if not box:
                    continue
                polygon = np.array(box, dtype=np.int32).reshape((-1, 1, 2))
                text_regions.append({
                    "text": text,
                    "confidence": round(float(conf), 4),
                    "box": box,
                    "bbox": rec_boxes[idx] if idx < len(rec_boxes) else [],
                    "polygon": polygon
                })

            logger.info(f"OCR raw parsed: {len(text_regions)} boxes")
            if merge_boxes:
                text_regions = self._merge_text_boxes(
                    text_regions,
                    max_col_gap=max_col_gap,
                    max_row_gap=max_row_gap,
                    reading_order=reading_order
                )
                logger.info(f"After merge: {len(text_regions)} boxes")
            return text_regions

        except Exception as e:
            logger.error(f"OCR parsing failed: {e}", exc_info=True)
            raise

    # ---------------- 竖排漫画专用合并 ----------------
    def _merge_text_boxes(
            self,
            text_regions: List[Dict[str, Any]],
            max_col_gap: int = 60,
            max_row_gap: int = 70,
            reading_order: str = "rtl"
    ) -> List[Dict[str, Any]]:
        """
        按「列中心距 + 垂直连续」合并，零水平重叠也可合并
        """
        n = len(text_regions)
        if n <= 1:
            return text_regions

        # 1. 统计每个框中心、边界、宽高
        def _stat(reg):
            xs = [p[0] for p in reg["box"]]
            ys = [p[1] for p in reg["box"]]
            return {"cx": (min(xs) + max(xs)) / 2,
                    "cy": (min(ys) + max(ys)) / 2,
                    "left": min(xs), "right": max(xs),
                    "top": min(ys), "bottom": max(ys),
                    "width": max(xs) - min(xs),
                    "height": max(ys) - min(ys)}

        stats = [_stat(r) for r in text_regions]

        # 2. 并查集
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            parent[find(x)] = find(y)

        # 3. 合并策略：列中心距小 + 垂直连续
        for i in range(n):
            for j in range(i + 1, n):
                s_i, s_j = stats[i], stats[j]
                col_gap = abs(s_i["cx"] - s_j["cx"])          # 列中心距
                row_gap = max(s_i["top"], s_j["top"]) - min(s_i["bottom"], s_j["bottom"])  # 垂直空隙
                if col_gap <= max_col_gap and row_gap <= max_row_gap:
                    union(i, j)

        # 4. 分组 & 组内排序（右->左，上->下）
        groups = {}
        for i in range(n):
            groups.setdefault(find(i), []).append(i)
        for g in groups.values():
            if reading_order == "rtl":
                g.sort(key=lambda i: (-stats[i]["cx"], stats[i]["top"]))
            else:
                g.sort(key=lambda i: (stats[i]["cx"], stats[i]["top"]))

        # 5. 合并每组
        merged = []
        for g in groups.values():
            regs = [text_regions[i] for i in g]
            merged_text = "".join(r["text"] for r in regs)
            avg_conf = round(sum(r["confidence"] for r in regs) / len(regs), 4)
            all_pts = np.vstack([np.array(r["box"], dtype=np.int32) for r in regs])
            x_min, y_min = all_pts.min(axis=0)
            x_max, y_max = all_pts.max(axis=0)
            outer_box = [
                [int(x_min), int(y_min)],
                [int(x_max), int(y_min)],
                [int(x_max), int(y_max)],
                [int(x_min), int(y_max)]
            ]
            polygon = np.array(outer_box, dtype=np.int32).reshape((-1, 1, 2))
            merged.append({
                "text": merged_text,
                "confidence": avg_conf,
                "box": outer_box,
                "bbox": [int(x_min), int(y_min), int(x_max), int(y_max)],
                "polygon": polygon
            })

        # 6. 整体再按阅读顺序排一次
        def _cx(reg): return sum(p[0] for p in reg["box"]) / 4
        def _top(reg): return min(p[1] for p in reg["box"])
        if reading_order == "rtl":
            merged.sort(key=lambda r: (-_cx(r), _top(r)))
        else:
            merged.sort(key=lambda r: (_cx(r), _top(r)))
        return merged