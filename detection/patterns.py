import re

# 1. البريد الإلكتروني
EMAIL_PATTERN = re.compile(
    r'(?P<value>\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)'
)

# 2. أرقام الهواتف
PHONE_PATTERN = re.compile(
    r'(?P<value>(?<![\d٠-٩۰-۹])\+?[\d٠-٩۰-۹](?:[\s().-]*[\d٠-٩۰-۹]){6,14}(?![\d٠-٩۰-۹]))'
)

# 3. كلمات المرور: تدعم وجود الفاصل أو عدمه، وكذلك "is / هو / هي"
PASSWORD_PATTERN = re.compile(
    r'(?:password|passcode|كلمة\s*المرور|كلمة\s*السر|الرقم\s*السري)'
    r'\s*(?::|=|：)?\s*(?:(?:is|هو|هي)\s+)?'
    r'(?P<value>[^\s,;|]+)',
    re.IGNORECASE
)

# 4. أرقام الهوية الوطنية، بما فيها الأرقام العربية والهندية
NATIONAL_ID_PATTERN = re.compile(
    r'(?:national\s*(?:id|identity)(?:\s*(?:number|no))?|'
    r'identity\s*(?:number|no)|id\s*(?:number|no)|'
    r'(?:رقم\s*)?الهوية(?:\s*الوطنية)?|'
    r'الرقم\s*الوطني|رقم\s*البطاقة\s*الشخصية|'
    r'رقم\s*البطاقة)'
    r'\s*[:#=\-]?\s*(?P<value>[A-Z0-9٠-٩۰-۹-]{5,20})',
    re.IGNORECASE
)

# 5. أرقام جوازات السفر
PASSPORT_PATTERN = re.compile(
    r'(?:passport\s*(?:number|no|id)?|'
    r'رقم\s*جواز\s*السفر|رقم\s*الجواز)'
    r'\s*[:#=\-]?\s*(?P<value>[A-Z0-9٠-٩۰-۹-]{5,15})',
    re.IGNORECASE
)

# 6. أرقام البطاقات المصرفية (التحقق النهائي بخوارزمية Luhn)
CARD_PATTERN = re.compile(
    r'(?P<value>(?<!\d)(?:\d[ -]?){12,18}\d(?!\d))'
)

# 7. أرقام الحسابات البنكية المحلية
BANK_ACCOUNT_PATTERN = re.compile(
    r'(?:bank\s*account|account\s*(?:number|no)|'
    r'رقم\s*الحساب|الحساب\s*البنكي)'
    r'\s*[:#=\-]?\s*(?P<value>[A-Z0-9-]{6,34})',
    re.IGNORECASE
)

# 8. أرقام الحسابات البنكية الدولية IBAN
IBAN_PATTERN = re.compile(
    r'(?P<value>\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b)',
    re.IGNORECASE
)

# 9. الاسم الكامل: يُكتشف عند وجود تسمية واضحة
NAME_PATTERN = re.compile(
    r'(?:الاسم\s*الكامل|الاسم|اسم\s*(?:المتقدم|الموظف|صاحب\s*الحساب)|'
    r'full\s*name|applicant\s*name|employee\s*name|name)'
    r'\s*[:：=]?\s*'
    r'(?P<value>[A-Za-z\u0600-\u06FF]+(?:[ \t]+[A-Za-z\u0600-\u06FF]+){1,4})',
    re.IGNORECASE
)

# 10. العنوان السكني: يُكتشف عند وجود تسمية واضحة
ADDRESS_PATTERN = re.compile(
    r'(?:العنوان\s*(?:السكني|الشخصي)?|مكان\s*السكن|'
    r'home\s*address|residential\s*address|address)'
    r'\s*[:：=]?\s*(?P<value>[^\r\n;|]{5,120})',
    re.IGNORECASE
)

# 11. تاريخ الميلاد بصيغ رقمية شائعة
DATE_OF_BIRTH_PATTERN = re.compile(
    r'(?:تاريخ\s*الميلاد|تاريخ\s*الولادة|الميلاد|'
    r'date\s*of\s*birth|birth\s*date|dob)'
    r'\s*[:：=]?\s*'
    r'(?P<value>(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|'
    r'(?:\d{4}[/-]\d{1,2}[/-]\d{1,2})|'
    r'(?:\d{1,2}\.\d{1,2}\.\d{2,4}))',
    re.IGNORECASE
)

# 12. اسم المستخدم
USERNAME_PATTERN = re.compile(
    r'(?:اسم\s*المستخدم|معرّف\s*المستخدم|username|user\s*name|login\s*name)'
    r'\s*[:：=]?\s*(?P<value>[A-Za-z0-9_.@-]{3,50})',
    re.IGNORECASE
)

# 13. الراتب (بيانات مالية شخصية)
SALARY_PATTERN = re.compile(
    r'(?:الراتب(?:\s*الشهري)?|salary|monthly\s*salary)'
    r'\s*[:：=]?\s*(?P<value>(?:[0-9٠-٩۰-۹][0-9٠-٩۰-۹,،.]*)'
    r'(?:\s*(?:ريال|ر\.ي|دولار|USD|YER))?)',
    re.IGNORECASE
)

# جمع الأنماط في قاموس واحد
PATTERNS = {
    "password": PASSWORD_PATTERN,
    "national_id": NATIONAL_ID_PATTERN,
    "passport": PASSPORT_PATTERN,
    "iban": IBAN_PATTERN,
    "bank_account": BANK_ACCOUNT_PATTERN,
    "credit_card": CARD_PATTERN,
    "email": EMAIL_PATTERN,
    "phone": PHONE_PATTERN,
    "full_name": NAME_PATTERN,
    "address": ADDRESS_PATTERN,
    "date_of_birth": DATE_OF_BIRTH_PATTERN,
    "username": USERNAME_PATTERN,
    "salary": SALARY_PATTERN,
}
