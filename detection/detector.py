import re
from detection.patterns import PATTERNS


# التحقق من صحة رقم البطاقة المصرفية باستخدام Luhn
def is_valid_card(number):
    digits = re.sub(r"[\s-]", "", number)

    if not digits.isdigit():
        return False

    total = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)

        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9

        total += n

    return total % 10 == 0


# التحقق من صحة رقم IBAN باستخدام MOD-97
def is_valid_iban(iban):
    iban = re.sub(r"\s+", "", iban).upper()

    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", iban):
        return False

    rearranged = iban[4:] + iban[:4]

    converted = ""
    for char in rearranged:
        if char.isdigit():
            converted += char
        else:
            converted += str(ord(char) - 55)

    remainder = 0
    for digit in converted:
        remainder = (remainder * 10 + int(digit)) % 97

    return remainder == 1


def detect_sensitive_data(text, allowed_types=None):
    """اكتشاف البيانات الحساسة وإرجاع نوعها وقيمتها ومواضعها داخل النص."""

    if not isinstance(text, str) or not text:
        return []

    if allowed_types is not None and len(allowed_types) == 0:
        return []

    priority = [
        "password",
        "national_id",
        "passport",
        "date_of_birth",
        "salary",
        "username",
        "full_name",
        "address",
        "iban",
        "bank_account",
        "credit_card",
        "email",
        "phone",
    ]

    # تحديد الأنواع المطلوب كشفها
    selected_types = (
        set(allowed_types)
        if allowed_types is not None
        else set(PATTERNS.keys())
    )

    detected_data = []

    specific_value_spans = []
    if "phone" in selected_types:
        for other_type, other_pattern in PATTERNS.items():
            if other_type == "phone":
                continue

            for other_match in other_pattern.finditer(text):
                other_start, other_end = other_match.span("value")
                if other_start < other_end:
                    specific_value_spans.append((other_start, other_end))

    for data_type in priority:
        if data_type not in PATTERNS:
            continue

        # تجاهل التصنيفات غير المختارة قبل معالجة التداخل
        if data_type not in selected_types:
            continue

        pattern = PATTERNS[data_type]

        for match in pattern.finditer(text):
            raw_value = match.group("value")
            value = raw_value.strip()
            start, end = match.span("value")

            leading_spaces = len(raw_value) - len(raw_value.lstrip())
            trailing_spaces = len(raw_value) - len(raw_value.rstrip())

            start += leading_spaces
            end -= trailing_spaces

            if not value:
                continue

            if data_type == "credit_card" and not is_valid_card(value):
                continue

            if data_type == "iban" and not is_valid_iban(value):
                continue

            if data_type == "phone" and any(
                other_start <= start and end <= other_end
                for other_start, other_end in specific_value_spans
            ):
                continue

            detected_data.append({
                "type": data_type,
                "value": value,
                "start": start,
                "end": end
            })

    priority_order = {
        data_type: index
        for index, data_type in enumerate(priority)
    }

    detected_data.sort(
        key=lambda item: (
            priority_order.get(item["type"], 99),
            -(item["end"] - item["start"])
        )
    )

    filtered_data = []

    for item in detected_data:
        overlaps = any(
            item["start"] < existing["end"]
            and item["end"] > existing["start"]
            for existing in filtered_data
        )

        if not overlaps:
            filtered_data.append(item)

    filtered_data.sort(
        key=lambda item: (item["start"], item["end"])
    )

    return filtered_data
