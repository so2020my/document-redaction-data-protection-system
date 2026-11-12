
from pathlib import Path
import pymupdf


def extract_lines(text):
    """
    استخراج أسطر النص مع الاحتفاظ بمواضعها داخل النص الأصلي.
    """
    lines = []
    current_position = 0

    for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        line_text = raw_line.rstrip("\r\n")

        lines.append({
            "line_number": line_number,
            "text": line_text,
            "start": current_position,
            "end": current_position + len(line_text)
        })

        current_position += len(raw_line)

    return lines


def read_pdf(file_path):
    """
    قراءة صفحات ملف PDF وإرجاع رقم كل صفحة والنص المستخرج منها وأسطره.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("الملف غير موجود.")

    if path.suffix.lower() != ".pdf":
        raise ValueError("نوع الملف غير مدعوم. يرجى اختيار ملف PDF.")

    try:
        with pymupdf.open(path) as document:
            pages = []

            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text()

                pages.append({
                    "page_number": page_number,
                    "text": page_text,
                    "lines": extract_lines(page_text)
                })

    except Exception as error:
        raise ValueError("تعذرت قراءة ملف PDF، ربما يكون تالفًا.") from error

    if not any(page["text"].strip() for page in pages):
        raise ValueError("ملف PDF لا يحتوي على نص قابل للاستخراج.")

    return pages
