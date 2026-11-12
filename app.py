# ========================================================
# نظام حماية المستندات
# الملف الرئيسي لتشغيل التطبيق والتنقل بين الصفحات
# ========================================================

import streamlit as st

# استيراد الدوال المسؤولة عن الواجهة من مجلد interface
from interface.pages import (
    load_css,
    initialize_session_state,
    render_sidebar,
    render_home_page,
    render_scan_page,
    render_masking_page,
    render_report_page
)

# --------------------------------------------------------
# 1. إعدادات الصفحة الأساسية
# يجب أن يكون هذا الأمر أول أمر خاص بـ Streamlit
# --------------------------------------------------------

st.set_page_config(
    page_title="نظام حماية المستندات",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# 2. تحميل تنسيقات CSS
# --------------------------------------------------------

load_css()

# --------------------------------------------------------
# 3. تهيئة متغيرات الجلسة
# --------------------------------------------------------

initialize_session_state()

# --------------------------------------------------------
# 4. عرض القائمة الجانبية
# --------------------------------------------------------

render_sidebar()

# --------------------------------------------------------
# 5. تحديد الصفحة التي يريد المستخدم عرضها
# --------------------------------------------------------

PAGE_ALIASES = {
    "home": "الرئيسية",
    "scan": "فحص المستند",
    "masking": "تعتيم البيانات",
    "report": "التقرير"
}

if "page" in st.query_params:
    q_page = st.query_params["page"]
    if q_page in PAGE_ALIASES:
        st.session_state.current_page = PAGE_ALIASES[q_page]
    elif q_page in PAGE_ALIASES.values():
        st.session_state.current_page = q_page

if st.query_params.get("demo") == "1":
    if not st.session_state.get("current_document"):
        st.session_state.current_document = {
            "file_name": "بيانات_الموظفين.txt",
            "file_size": "2.40 KB",
            "file_type": "txt",
            "upload_path": "uploads/بيانات_الموظفين.txt",
            "content": "تقرير الموظفين السري\nاسم الموظف: أحمد محمد سالم\nالبريد الإلكتروني: ahmed.salem@company.com\nرقم الهاتف: +966501234567\nرقم الهوية الوطنية: 1098765432\nرقم الحساب البنكي: 12345678901234\nIBAN: SA0380000000608010167519\nانتهى التقرير.",
            "pages": None
        }
        st.session_state.scan_completed = True
        st.session_state.masking_applied = True
        st.session_state.masking_view_mode = "masked"
        st.session_state.redacted_content = "تقرير الموظفين السري\nاسم الموظف: أحمد محمد سالم\nالبريد الإلكتروني: ********\nرقم الهاتف: ********\nرقم الهوية الوطنية: ********\nرقم الحساب البنكي: ********\nIBAN: ********\nانتهى التقرير."
        st.session_state.redacted_file_path = "processed/redacted_بيانات_الموظفين.txt"
        st.session_state.detected_data = [
            {"type": "email", "value": "ahmed.salem@company.com", "start": 56, "end": 79},
            {"type": "phone", "value": "+966501234567", "start": 91, "end": 104},
            {"type": "national_id", "value": "1098765432", "start": 125, "end": 135},
            {"type": "bank_account", "value": "12345678901234", "start": 155, "end": 169},
            {"type": "iban", "value": "SA0380000000608010167519", "start": 176, "end": 200}
        ]
        st.session_state.detected_count = 5

current_page = st.session_state.current_page

# --------------------------------------------------------
# 6. التنقل بين صفحات النظام
# --------------------------------------------------------

if current_page == "الرئيسية":

    # عرض الصفحة الرئيسية
    render_home_page()

elif current_page == "فحص المستند":

    # عرض صفحة فحص المستند
    render_scan_page()

elif current_page == "تعتيم البيانات":

    # عرض صفحة تعتيم البيانات الحساسة
    render_masking_page()

elif current_page == "التقرير":

    # عرض صفحة التقرير النهائي
    render_report_page()


else:

    # العودة إلى الصفحة الرئيسية عند وجود اسم صفحة غير معروف
    st.session_state.current_page = "الرئيسية"
    st.rerun()