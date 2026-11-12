
import unittest

from detection.detector import detect_sensitive_data


class TestDetector(unittest.TestCase):

    def check_detection(self, text, expected_type):
        results = detect_sensitive_data(text)

        found_types = [item["type"] for item in results]

        self.assertIn(
            expected_type,
            found_types,
            f"لم يتم اكتشاف النوع: {expected_type}"
        )

    def test_email(self):
        self.check_detection(
            "Email: user@gmail.com",
            "email"
        )

    def test_phone(self):
        self.check_detection(
            "Phone: +967771234567",
            "phone"
        )

    def test_password(self):
        self.check_detection(
            "Password: Abc12345",
            "password"
        )

    def test_national_id(self):
        self.check_detection(
            "National ID: AB1234567",
            "national_id"
        )

    def test_passport(self):
        self.check_detection(
            "Passport Number: A1234567",
            "passport"
        )

    def test_credit_card(self):
        self.check_detection(
            "Card: 4532015112830366",
            "credit_card"
        )

    def test_bank_account(self):
        self.check_detection(
            "Account Number: 12345678901234",
            "bank_account"
        )

    def test_iban(self):
        self.check_detection(
            "IBAN: GB29NWBK60161331926819",
            "iban"
        )

    
    # اختبار اكتشاف عدة بيانات في نص واحد
    def test_multiple_data(self):
        text = (
            "Email: user@gmail.com, "
            "Passport Number: A1234567"
        )

        results = detect_sensitive_data(text)
        found_types = [item["type"] for item in results]

        self.assertIn("email", found_types)
        self.assertIn("passport", found_types)

    # اختبار صحة مواقع البيانات المكتشفة
    def test_detection_positions(self):
        text = "Email: user@gmail.com"

        results = detect_sensitive_data(text)

        email = next(
            item for item in results
            if item["type"] == "email"
        )

        self.assertEqual(
            text[email["start"]:email["end"]],
            email["value"]
        )

    # اختبار رفض رقم بطاقة غير صحيح
    def test_invalid_card(self):
        text = "Card: 4532015112830367"

        results = detect_sensitive_data(text)

        self.assertNotIn(
            "credit_card",
            [item["type"] for item in results]
        )

    # اختبار رفض IBAN غير صحيح
    def test_invalid_iban(self):
        text = "IBAN: GB00NWBK60161331926819"

        results = detect_sensitive_data(text)

        self.assertNotIn(
            "iban",
            [item["type"] for item in results]
        )

    # اختبار عدم تكرار النتيجة المتداخلة
    def test_no_duplicate_detection(self):
        text = "Account Number: 4532015112830366"

        results = detect_sensitive_data(text)

        matching_results = [
            item for item in results
            if item["value"] == "4532015112830366"
        ]

        self.assertEqual(len(matching_results), 1)

    def test_redact_text_and_save_to_database(self):
        from redaction.txt_redactor import redact_text

        text = "Email: test@example.com"

        redacted_text, detected_data = redact_text(
            text,
            "test_integration.txt"
        )

        self.assertIn("********", redacted_text)
        self.assertNotIn("test@example.com", redacted_text)
        self.assertEqual(len(detected_data), 1)


if __name__ == "__main__":
    unittest.main()
