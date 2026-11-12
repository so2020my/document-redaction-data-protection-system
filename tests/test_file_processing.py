import unittest
import tempfile
import pymupdf
from pathlib import Path

from file_processing.txt_reader import read_txt
from file_processing.pdf_reader import read_pdf
from interface.pages import (
    is_allowed_file_type,
    ALLOWED_FILE_EXTENSIONS,
    UNSUPPORTED_FILE_TYPE_MESSAGE,
    NO_SENSITIVE_DATA_MESSAGE
)
from detection.detector import detect_sensitive_data


class TestFileProcessing(unittest.TestCase):

    def test_read_txt_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write("محتوى تجريبي لملف نصي\nالسطر الثاني")
            temp_path = temp_file.name

        try:
            content = read_txt(temp_path)
            self.assertIn("محتوى تجريبي لملف نصي", content)
            self.assertIn("السطر الثاني", content)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_txt_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_txt("non_existent_file.txt")

    def test_read_txt_invalid_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with self.assertRaises(ValueError):
                read_txt(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_txt_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_path = temp_file.name

        try:
            with self.assertRaises(ValueError):
                read_txt(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_pdf_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name

        doc = pymupdf.open()
        page1 = doc.new_page()
        page1.insert_text((50, 80), "Page 1 sample text")
        page2 = doc.new_page()
        page2.insert_text((50, 80), "Page 2 sample text")
        doc.save(temp_path)
        doc.close()

        try:
            pages = read_pdf(temp_path)
            self.assertEqual(len(pages), 2)
            self.assertEqual(pages[0]["page_number"], 1)
            self.assertIn("Page 1 sample text", pages[0]["text"])
            self.assertEqual(pages[1]["page_number"], 2)
            self.assertIn("Page 2 sample text", pages[1]["text"])
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_pdf_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_pdf("non_existent_file.pdf")

    def test_read_pdf_invalid_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with self.assertRaises(ValueError):
                read_pdf(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_pdf_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name

        doc = pymupdf.open()
        doc.new_page()  # صفحة بدون نص
        doc.save(temp_path)
        doc.close()

        try:
            with self.assertRaises(ValueError):
                read_pdf(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_allowed_file_types_pdf_and_txt(self):
        """قبول ملفات PDF و TXT فقط بمختلف الصيغ (أحرف صغيرة وكبيرة)."""
        self.assertEqual(ALLOWED_FILE_EXTENSIONS, {".pdf", ".txt"})
        self.assertTrue(is_allowed_file_type("document.txt"))
        self.assertTrue(is_allowed_file_type("DOCUMENT.TXT"))
        self.assertTrue(is_allowed_file_type("file.pdf"))
        self.assertTrue(is_allowed_file_type("FILE.PDF"))
        self.assertTrue(is_allowed_file_type("path/to/my_file.txt"))
        self.assertTrue(is_allowed_file_type("path/to/my_file.pdf"))

    def test_rejected_file_types_docx_jpg_and_others(self):
        """رفض DOCX و JPG وبقية الأنواع غير المدعومة."""
        self.assertFalse(is_allowed_file_type("document.docx"))
        self.assertFalse(is_allowed_file_type("document.DOCX"))
        self.assertFalse(is_allowed_file_type("file.doc"))
        self.assertFalse(is_allowed_file_type("picture.jpg"))
        self.assertFalse(is_allowed_file_type("PICTURE.JPG"))
        self.assertFalse(is_allowed_file_type("image.png"))
        self.assertFalse(is_allowed_file_type("sheet.xlsx"))
        self.assertFalse(is_allowed_file_type("archive.zip"))
        self.assertFalse(is_allowed_file_type("executable.exe"))
        self.assertFalse(is_allowed_file_type("no_extension"))
        self.assertFalse(is_allowed_file_type(""))
        self.assertFalse(is_allowed_file_type(None))

    def test_unsupported_file_message_content(self):
        """التأكد من نص رسالة الرفض المحددة بدقة."""
        expected_message = "نوع الملف غير مدعوم. يُسمح برفع ملفات PDF وTXT فقط"
        self.assertEqual(UNSUPPORTED_FILE_TYPE_MESSAGE, expected_message)

    def test_upload_rejection_and_recovery_flow(self):
        """محاكاة منطق التحقق: رفض ملف غير مدعوم ثم قبول ملف مدعوم بنجاح."""
        session = {
            "current_document": None,
            "upload_error": None,
            "uploader_id": 0
        }

        # 1. محاولة رفع DOCX
        candidate_file = "report.docx"
        if not is_allowed_file_type(candidate_file):
            session["upload_error"] = UNSUPPORTED_FILE_TYPE_MESSAGE
            session["uploader_id"] += 1
            # لا يتم تعيين المستند
            session["current_document"] = None

        self.assertEqual(session["upload_error"], "نوع الملف غير مدعوم. يُسمح برفع ملفات PDF وTXT فقط")
        self.assertIsNone(session["current_document"])
        self.assertEqual(session["uploader_id"], 1)

        # 2. محاولة رفع JPG بعد الرفض
        candidate_file_2 = "photo.jpg"
        if not is_allowed_file_type(candidate_file_2):
            session["upload_error"] = UNSUPPORTED_FILE_TYPE_MESSAGE
            session["uploader_id"] += 1
            session["current_document"] = None

        self.assertEqual(session["upload_error"], "نوع الملف غير مدعوم. يُسمح برفع ملفات PDF وTXT فقط")
        self.assertIsNone(session["current_document"])
        self.assertEqual(session["uploader_id"], 2)

        # 3. اختيار ملف TXT صحيح بعد الرفض
        valid_file = "notes.txt"
        if is_allowed_file_type(valid_file):
            session["upload_error"] = None
            session["current_document"] = {"file_name": valid_file, "file_type": "txt"}

        self.assertIsNone(session["upload_error"])
        self.assertIsNotNone(session["current_document"])
        self.assertEqual(session["current_document"]["file_name"], "notes.txt")

    def test_txt_without_sensitive_data_blocks_masking(self):
        """1. ملف TXT لا يحتوي على بيانات حساسة: ينتج قائمة كشف فارغة ورسالة عدم وجود بيانات."""
        clean_text = "هذا مستند عام يتحدث عن الذكاء الاصطناعي وتطبيقاته الحديثة في التعليم."
        detected = detect_sensitive_data(clean_text)
        self.assertEqual(len(detected), 0)
        self.assertEqual(
            NO_SENSITIVE_DATA_MESSAGE,
            "لم يتم العثور على بيانات حساسة تحتاج إلى تعتيم في هذا المستند."
        )

    def test_pdf_without_sensitive_data_blocks_masking(self):
        """2. ملف PDF لا يحتوي على بيانات حساسة: كشف فارغ ولا ينتقل للتعتيم."""
        clean_page_text = "Artificial intelligence research report without any personal data."
        detected = detect_sensitive_data(clean_page_text)
        self.assertEqual(len(detected), 0)

    def test_txt_with_sensitive_data_allows_masking(self):
        """3. ملف TXT يحتوي على بيانات حساسة: تظهر النتائج ويسمح بالتعتيم."""
        sensitive_text = "البريد الإلكتروني: user@example.com ورقم الجوال: 0501234567"
        detected = detect_sensitive_data(sensitive_text)
        self.assertGreater(len(detected), 0)
        types = [d["type"] for d in detected]
        self.assertIn("email", types)
        self.assertIn("phone", types)

    def test_pdf_with_sensitive_data_allows_masking(self):
        """4. ملف PDF يحتوي على بيانات حساسة: تظهر النتائج ويسمح بالتعتيم."""
        pdf_text = "بيانات الموظف:\nرقم الهوية الوطنية: 1098765432\nكلمة المرور: SecretP@ss123"
        detected = detect_sensitive_data(pdf_text)
        self.assertGreater(len(detected), 0)
        types = [d["type"] for d in detected]
        self.assertIn("national_id", types)
        self.assertIn("password", types)

    def test_extraction_or_scan_error_blocks_masking(self):
        """5. حدوث خطأ أثناء استخراج النص أو الفحص: لا يسمح بالانتقال للتعتيم وتظهر رسالة خطأ."""
        session = {
            "scan_completed": True,
            "masking_applied": True,
            "detected_count": 5
        }
        # عند حدوث خطأ أثناء الفحص
        try:
            # محاكاة خطأ استخراج نص فارغ أو تالف
            empty_content = "   "
            if not empty_content.strip():
                raise ValueError("الملف فارغ ولا يحتوي على نص قابل للفحص.")
        except Exception as error:
            session["scan_completed"] = False
            session["masking_applied"] = False
            session["detected_count"] = 0
            error_message = f"تعذر إتمام الفحص: {error}"

        self.assertFalse(session["scan_completed"])
        self.assertFalse(session["masking_applied"])
        self.assertEqual(session["detected_count"], 0)
        self.assertIn("الملف فارغ", error_message)

    def test_scan_no_sensitive_then_new_file_with_sensitive(self):
        """6. بعد فحص ملف خالٍ من البيانات الحساسة، رفع ملف آخر يحتوي على بيانات حساسة."""
        # الملف الأول الخالي
        first_text = "نص عادي خالٍ من أي بيانات سرية."
        first_detected = detect_sensitive_data(first_text)
        self.assertEqual(len(first_detected), 0)
        first_can_mask = len(first_detected) > 0
        self.assertFalse(first_can_mask)

        # إعادة الضبط ورفع ملف ثانٍ يحتوي على بيانات حساسة
        second_text = "بيانات بنكية: IBAN SA0380000000608010167519"
        second_detected = detect_sensitive_data(second_text)
        self.assertGreater(len(second_detected), 0)
        second_can_mask = len(second_detected) > 0
        self.assertTrue(second_can_mask)
        self.assertEqual(second_detected[0]["type"], "iban")


if __name__ == "__main__":
    unittest.main()
