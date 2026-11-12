import unittest
import os
import tempfile
from pathlib import Path
import pymupdf

from detection.detector import detect_sensitive_data
from redaction.txt_redactor import redact_text
from redaction.pdf_redactor import redact_pdf
from interface.pages import get_allowed_types_from_categories


SENSITIVE_SAMPLES = {
    "email": "Email: alice@example.com",
    "phone": "Phone: +1 (202) 555-0101",
    "national_id": "National ID: AB1234567",
    "passport": "Passport Number: P12345678",
    "full_name": "Full name: John Doe",
    "date_of_birth": "Date of birth: 1990-04-15",
    "address": "Address: 42 West Avenue",
    "credit_card": "Card: 4532015112830366",
    "bank_account": "Account Number: 12345678901234",
    "iban": "IBAN: GB29NWBK60161331926819",
    "salary": "Salary: 75000 USD",
    "password": "Password: SecretPass99",
    "username": "Username: user_123",
}

SENSITIVE_TYPES = list(SENSITIVE_SAMPLES)


class TestCategoryRedaction(unittest.TestCase):

    def test_card_5555_full_detection_and_in_place_redaction(self):
        """التأكد من أن رقم البطاقة 5555 5555 5555 4444 يُكتشف كاملًا ويُعتّم في موضعه الصحيح."""
        text = "رقم البطاقة: 5555 5555 5555 4444 ينتهي في 2028"
        results = detect_sensitive_data(text)

        card_item = next((item for item in results if item["type"] == "credit_card"), None)
        self.assertIsNotNone(card_item, "يجب اكتشاف البطاقة كـ credit_card")
        self.assertEqual(card_item["value"], "5555 5555 5555 4444")

        redacted, _ = redact_text(text)
        self.assertNotIn("5555 5555 5555 4444", redacted)
        self.assertNotIn("4444", redacted.replace("2028", ""))
        self.assertEqual(redacted, "رقم البطاقة: ******** ينتهي في 2028")

    def test_password_without_colon(self):
        """التأكد من أن كلمة المرور التي تسبقها عبارة «كلمة المرور» تُكتشف حتى دون وجود نقطتين."""
        text1 = "كلمة المرور Abc12345 لدخول النظام"
        results1 = detect_sensitive_data(text1)
        self.assertTrue(any(item["type"] == "password" and item["value"] == "Abc12345" for item in results1))

        redacted1, _ = redact_text(text1)
        self.assertEqual(redacted1, "كلمة المرور ******** لدخول النظام")

        text2 = "كلمة المرور: SecretPass99"
        results2 = detect_sensitive_data(text2)
        self.assertTrue(any(item["type"] == "password" and item["value"] == "SecretPass99" for item in results2))

    def test_email_only_category(self):
        """اختيار البريد الإلكتروني فقط والتأكد من بقاء الهاتف دون تعتيم."""
        text = "البريد: user@example.com والهاتف: +966501234567"
        redacted, detected = redact_text(text, allowed_types=["email"])

        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["type"], "email")
        self.assertNotIn("user@example.com", redacted)
        self.assertIn("+966501234567", redacted)
        self.assertEqual(redacted, "البريد: ******** والهاتف: +966501234567")

    def test_phone_only_category(self):
        """اختيار الهاتف فقط والتأكد من بقاء البريد الإلكتروني دون تعتيم."""
        text = "البريد: user@example.com والهاتف: +966501234567"
        redacted, detected = redact_text(text, allowed_types=["phone"])

        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["type"], "phone")
        self.assertIn("user@example.com", redacted)
        self.assertNotIn("+966501234567", redacted)
        self.assertEqual(redacted, "البريد: user@example.com والهاتف: ********")

    def test_both_email_and_phone_category(self):
        """اختيار البريد والهاتف معًا والتأكد من تعتيم الاثنين فقط."""
        text = "البريد: user@example.com، الهاتف: +966501234567، الهوية: 1098765432"
        redacted, detected = redact_text(text, allowed_types=["email", "phone"])

        types = [d["type"] for d in detected]
        self.assertIn("email", types)
        self.assertIn("phone", types)
        self.assertNotIn("national_id", types)

        self.assertNotIn("user@example.com", redacted)
        self.assertNotIn("+966501234567", redacted)
        self.assertIn("1098765432", redacted)
        self.assertEqual(redacted, "البريد: ********، الهاتف: ********، الهوية: 1098765432")

    def test_allowed_types_are_mapped_independently(self):
        categories = {data_type: False for data_type in SENSITIVE_TYPES}
        categories["email"] = True
        self.assertEqual(get_allowed_types_from_categories(categories), ["email"])

        categories = {data_type: True for data_type in SENSITIVE_TYPES}
        self.assertEqual(
            get_allowed_types_from_categories(categories),
            SENSITIVE_TYPES
        )

    def test_each_type_can_be_redacted_without_other_types(self):
        text = (
            "Ordinary notes remain unchanged.\n"
            + "\n".join(SENSITIVE_SAMPLES.values())
        )

        for selected_type, selected_line in SENSITIVE_SAMPLES.items():
            with self.subTest(data_type=selected_type):
                redacted, detected = redact_text(
                    text,
                    allowed_types=[selected_type]
                )
                self.assertEqual(
                    [item["type"] for item in detected],
                    [selected_type]
                )
                self.assertEqual(
                    redacted,
                    text.replace(
                        selected_line.split(": ", 1)[1],
                        "********",
                        1
                    )
                )
                self.assertIn("Ordinary notes remain unchanged.", redacted)
                for other_type, other_line in SENSITIVE_SAMPLES.items():
                    if other_type != selected_type:
                        self.assertIn(
                            other_line.split(": ", 1)[1],
                            redacted
                        )

    def test_all_thirteen_types_are_detected_and_redacted(self):
        text = "\n".join(SENSITIVE_SAMPLES.values())
        redacted, detected = redact_text(
            text,
            allowed_types=SENSITIVE_TYPES
        )

        self.assertEqual(
            {item["type"] for item in detected},
            set(SENSITIVE_TYPES)
        )
        self.assertEqual(len(detected), len(SENSITIVE_TYPES))
        self.assertEqual(redacted.count("********"), len(SENSITIVE_TYPES))
        self.assertTrue(all(
            text[item["start"]:item["end"]] == item["value"]
            for item in detected
        ))
        self.assertTrue(all(
            previous["end"] <= current["start"]
            for previous, current in zip(detected, detected[1:])
        ))

    def test_all_thirteen_types_are_detected_by_default(self):
        detected = detect_sensitive_data(
            "\n".join(SENSITIVE_SAMPLES.values())
        )
        self.assertEqual(
            {item["type"] for item in detected},
            set(SENSITIVE_TYPES)
        )

    def test_phone_selection_does_not_capture_labeled_non_phone_values(self):
        text = (
            "Phone: +1 (202) 555-0101\n"
            "National ID: 1098765432\n"
            "Date of birth: 1990-04-15\n"
            "Account Number: 4532015112830366"
        )
        redacted, detected = redact_text(text, allowed_types=["phone"])

        self.assertEqual([item["type"] for item in detected], ["phone"])
        self.assertEqual(
            redacted,
            "Phone: ********\n"
            "National ID: 1098765432\n"
            "Date of birth: 1990-04-15\n"
            "Account Number: 4532015112830366"
        )

    def test_no_category_selected(self):
        """عدم اختيار أي تصنيف والتأكد من عدم تنفيذ التعتيم."""
        text = "البريد: user@example.com والهاتف: +966501234567"
        redacted, detected = redact_text(text, allowed_types=[])

        self.assertEqual(len(detected), 0)
        self.assertEqual(redacted, text)

    def test_in_place_txt_redaction_and_paragraph_structure(self):
        """التأكد من ظهور النجوم في مواضع القيم الأصلية والحفاظ على ترتيب النص والفقرات في TXT."""
        text = (
            "الفقرة الأولى:\n"
            "الاسم: محمد علي\n"
            "البريد: mohamed@domain.com\n\n"
            "الفقرة الثانية:\n"
            "الهاتف: +966551122334\n"
            "خاتمة التقرير."
        )

        redacted, detected = redact_text(text)
        expected = (
            "الفقرة الأولى:\n"
            "الاسم: ********\n"
            "البريد: ********\n\n"
            "الفقرة الثانية:\n"
            "الهاتف: ********\n"
            "خاتمة التقرير."
        )
        self.assertEqual(redacted, expected)
        name_item = next(
            item for item in detected
            if item["type"] == "full_name"
        )
        self.assertEqual(name_item["line_number"], 2)
        self.assertEqual(name_item["start_column"], 8)
        self.assertEqual(name_item["end_column"], 15)

    def test_pdf_in_place_redaction_and_structure(self):
        """التأكد من ظهور النجوم في مواضع القيم الأصلية داخل معاينة PDF والحفاظ على الترتيب."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf_in:
            in_path = tf_in.name
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf_out:
            out_path = tf_out.name

        try:
            doc = pymupdf.open()
            page = doc.new_page()
            sample_text = (
                "Full name: John Doe\n"
                "Email: ahmed@gmail.com\n"
                "Phone: +966501234567\n"
                "National ID: AB1234567\n"
                "End."
            )
            page.insert_text((50, 80), sample_text, fontsize=12)
            doc.save(in_path)
            doc.close()

            pages_data = [{"page_number": 1, "text": sample_text}]
            res = redact_pdf(in_path, out_path, pages_data, allowed_types=["email", "phone"])

            self.assertTrue(os.path.exists(out_path))
            self.assertEqual(res["detected_count"], 2)
            self.assertTrue(all(
                item["page_number"] == 1
                and item["line_number"] == 2 + (item["type"] == "phone")
                and len(item["rect"]) == 4
                for item in res["detected_data"]
            ))

            # التحقق من أن النص المعتم للمعاينة يحتوي على النجوم في مواضعها الصحيحة
            redacted_preview = res["redacted_text"]
            self.assertIn("Email: ********", redacted_preview)
            self.assertIn("Phone: ********", redacted_preview)
            self.assertNotIn("ahmed@gmail.com", redacted_preview)
            self.assertNotIn("+966501234567", redacted_preview)
            self.assertIn("John Doe", redacted_preview)
            self.assertIn("AB1234567", redacted_preview)
            # التأكد من عدم تراكم النجوم في نهاية النص
            self.assertFalse(redacted_preview.strip().endswith("********\n********"))

            redacted_document = pymupdf.open(out_path)
            redacted_pdf_text = redacted_document[0].get_text()
            redacted_document.close()
            self.assertNotIn("ahmed@gmail.com", redacted_pdf_text)
            self.assertNotIn("+966501234567", redacted_pdf_text)
            self.assertIn("John Doe", redacted_pdf_text)
            self.assertIn("AB1234567", redacted_pdf_text)
        finally:
            Path(in_path).unlink(missing_ok=True)
            Path(out_path).unlink(missing_ok=True)

    def test_pdf_redactor_supports_all_thirteen_types(self):
        sample_text = "\n".join(SENSITIVE_SAMPLES.values())
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "all_types.pdf"
            output_path = Path(temp_dir) / "redacted_all_types.pdf"

            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((50, 50), sample_text, fontsize=8)
            document.save(input_path)
            document.close()

            result = redact_pdf(
                str(input_path),
                str(output_path),
                [{"page_number": 1, "text": sample_text}]
            )

            self.assertEqual(result["detected_count"], 13)
            self.assertEqual(
                {item["type"] for item in result["detected_data"]},
                set(SENSITIVE_TYPES)
            )
            self.assertTrue(all(
                item["page_number"] == 1 and len(item["rect"]) == 4
                for item in result["detected_data"]
            ))
            for sample_line in SENSITIVE_SAMPLES.values():
                value = sample_line.split(": ", 1)[1]
                self.assertNotIn(value, result["redacted_text"])
            self.assertEqual(
                result["redacted_text"].count("********"),
                len(SENSITIVE_TYPES)
            )


if __name__ == "__main__":
    unittest.main()
