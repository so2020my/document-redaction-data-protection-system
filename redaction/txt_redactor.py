
from detection.detector import detect_sensitive_data
from database.db import save_sensitive_data


def redact_text(text, file_name=None, allowed_types=None):
    """
    اكتشاف البيانات الحساسة وتعتيمها بثماني نجوم ثابتة في مواضعها الأصلية،
    وحفظ البيانات الأصلية في قاعدة البيانات.
    """

    detected_data = detect_sensitive_data(text, allowed_types=allowed_types)

    # تجهيز مواقع الأسطر داخل النص
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

    # إضافة رقم السطر والأعمدة لكل نتيجة كشف
    for item in detected_data:
        matching_line = next(
            (
                line for line in lines
                if line["start"] <= item["start"] < line["end"]
            ),
            None
        )

        if matching_line:
            item["line_number"] = matching_line["line_number"]
            item["start_column"] = item["start"] - matching_line["start"] + 1
            item["end_column"] = item["end"] - matching_line["start"]
        else:
            item["line_number"] = None
            item["start_column"] = None
            item["end_column"] = None


    redacted_text = text

    # التعتيم من نهاية النص إلى بدايته
    for item in sorted(
        detected_data,
        key=lambda x: x["start"],
        reverse=True
    ):
        start = item["start"]
        end = item["end"]

        redacted_text = (
            redacted_text[:start]
            + "********"
            + redacted_text[end:]
        )

    # حفظ البيانات الحساسة في قاعدة البيانات
    if file_name and detected_data:
        save_sensitive_data(file_name, detected_data)

    return redacted_text, detected_data
