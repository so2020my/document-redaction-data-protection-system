
import unittest
import os
import pymupdf

from redaction.txt_redactor import redact_text
from redaction.pdf_redactor import redact_pdf


class TestRedaction(unittest.TestCase):

    def test_fixed_stars_redaction(self):
        text = "Email: ahmed@gmail.com, Password: 1234567890"

        redacted_text, detected_data = redact_text(text)

        self.assertNotIn("ahmed@gmail.com", redacted_text)
        self.assertNotIn("1234567890", redacted_text)
        self.assertEqual(redacted_text.count("********"), 2)

    def test_pdf_redaction(self):

        input_path = "tests/sample.pdf"
        output_path = "tests/redacted_sample.pdf"

        # إنشاء ملف PDF تجريبي
        doc = pymupdf.open()
        page = doc.new_page()

        page.insert_text(
            (50, 80),
            "Email: ahmed@gmail.com",
            fontsize=12
        )

        doc.save(input_path)
        doc.close()

        # بيانات تجريبية بالشكل المتفق عليه مع الطالبة الثانية
        pages = [
            {
                "page_number": 1,
                "text": "Email: ahmed@gmail.com"
            }
        ]

        result = redact_pdf(input_path, output_path, pages)

        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(result["detected_count"], 1)

        doc = pymupdf.open(output_path)
        redacted_text = doc[0].get_text()
        doc.close()

        self.assertNotIn("ahmed@gmail.com", redacted_text)
        self.assertIn("********", redacted_text)

        # حذف ملفات PDF التجريبية بعد انتهاء الاختبار
        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)


if __name__ == "__main__":
    unittest.main()
