
import pymupdf
from detection.detector import detect_sensitive_data
from database.db import save_sensitive_data
from pathlib import Path


def redact_pdf(input_path, output_path, pages, allowed_types=None):
    """
    اكتشاف البيانات الحساسة في PDF وإزالتها فعليًا،
    ثم وضع ثماني نجوم مكان كل قيمة وحفظ بياناتها في SQLite،
    مع الحفاظ على النص المعتم في مواضعه الأصلية.
    """

    doc = pymupdf.open(input_path)
    detected_data = []
    redacted_pages_text = []

    for page_data in pages:

        page_number = page_data["page_number"]
        text = page_data["text"]

        # تجهيز مواقع الأسطر داخل نص الصفحة
        lines = []
        current_position = 0

        for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
            line_text = raw_line.rstrip("\r\n")

            lines.append({
                "line_number": line_number,
                "start": current_position,
                "end": current_position + len(line_text)
            })

            current_position += len(raw_line)


        # اكتشاف البيانات الحساسة وفق التصنيفات المسموح بها فقط
        sensitive_items = detect_sensitive_data(text, allowed_types=allowed_types)

        # استبدال كل قيمة حساسة بالنجوم في موضعها الأصلي داخل الصفحة
        page_redacted_text = text
        for item in sorted(sensitive_items, key=lambda x: x["start"], reverse=True):
            page_redacted_text = (
                page_redacted_text[:item["start"]]
                + "********"
                + page_redacted_text[item["end"]:]
            )
        redacted_pages_text.append(f"--- صفحة {page_number} ---\n{page_redacted_text}")

        # الوصول إلى الصفحة المطلوبة
        page = doc[page_number - 1]

        # حفظ مواقع البيانات قبل إزالتها
        redaction_locations = []

        for item in sensitive_items:

            value = item["value"]
            locations = page.search_for(value)

            for rect in locations:

                page.add_redact_annot(
                    rect,
                    fill=(1, 1, 1)
                )

                redaction_locations.append({
                    "rect": rect,
                    "item": item
                })

        # إزالة النصوص الأصلية فعليًا
        page.apply_redactions()

        # كتابة النجوم في المواقع المحفوظة
        for location in redaction_locations:

            rect = location["rect"]
            item = location["item"]

            stars = "********"
            fontsize = 8

            x = rect.x0
            y = rect.y1 - 2

            page.insert_text(
                pymupdf.Point(x, y),
                stars,
                fontsize=fontsize,
                fontname="helv",
                color=(0, 0, 0)
            )

            
            # تحديد السطر الذي تقع فيه البيانات الحساسة
            line_number = next(
                (
                    line["line_number"]
                    for line in lines
                    if line["start"] <= item["start"] < line["end"]
                ),
                None
            )

            
            # تحديد السطر الذي تقع فيه البيانات الحساسة
            line_number = next(
                (
                    line["line_number"]
                    for line in lines
                    if line["start"] <= item["start"] < line["end"]
                ),
                None
            )

            
            # تحديد السطر الذي تقع فيه البيانات الحساسة
            line_number = next(
                (
                    line["line_number"]
                    for line in lines
                    if line["start"] <= item["start"] < line["end"]
                ),
                None
            )

            
            # تحديد السطر الذي تقع فيه البيانات الحساسة
            line_number = next(
                (
                    line["line_number"]
                    for line in lines
                    if line["start"] <= item["start"] < line["end"]
                ),
                None
            )

            
            # تحديد السطر الذي تقع فيه البيانات الحساسة
            line_number = next(
                (
                    line["line_number"]
                    for line in lines
                    if line["start"] <= item["start"] < line["end"]
                ),
                None
            )

            detected_data.append({
                "page_number": page_number,
                "line_number": line_number,
                "type": item["type"],
                "value": item["value"],
                "start": item["start"],
                "end": item["end"],
                "rect": [
                    rect.x0,
                    rect.y0,
                    rect.x1,
                    rect.y1
                ]
            })



    # حفظ الملف الجديد
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    # حفظ البيانات الحساسة في قاعدة البيانات
    if detected_data:
        save_sensitive_data(
            Path(input_path).name,
            detected_data
        )

    return {
        "output_path": output_path,
        "detected_count": len(detected_data),
        "detected_data": detected_data,
        "redacted_text": "\n\n".join(redacted_pages_text)
    }
