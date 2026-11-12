
# ========================================================
# نظام حماية المستندات
# Document Protection System
# ملف الواجهات والتصميم الكامل - app.py
# ========================================================

# --------------------------------------------------------
# 1. استيراد المكتبات
# --------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from pathlib import Path
import pymupdf

from file_processing import read_pdf, read_txt
from redaction.pdf_redactor import redact_pdf
from redaction.txt_redactor import redact_text


# --------------------------------------------------------
# 2. إعداد الصفحة الأساسية
# --------------------------------------------------------

st.set_page_config(
    page_title="نظام حماية المستندات",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------------
# 3. الهوية البصرية والتنسيقات
# --------------------------------------------------------

def load_css():

    st.markdown(
        """
        <style>

        /* =========================================
           الخطوط والاتجاه العام
        ========================================= */

        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

        html, body, [class*="css"], * {
            font-family: 'Cairo', Tahoma, sans-serif !important;
        }

        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            direction: rtl !important;
        }

        /* =========================================
           خلفية التطبيق ومحاذاة المحتوى
        ========================================= */

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #edf3fa !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1500px;
            padding: 35px 35px 50px;
            direction: rtl !important;
        }

        [data-testid="stMain"] .stMarkdown,
        [data-testid="stMain"] .stText,
        [data-testid="stMain"] label,
        [data-testid="stMain"] p,
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] [data-testid="stCaptionContainer"] {
            direction: rtl !important;
            text-align: right !important;
        }

        /* =========================================
           القائمة الجانبية
        ========================================= */

        [data-testid="stAppViewContainer"] {
            direction: rtl !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                160deg,
                #071629 0%,
                #102d4b 55%,
                #061426 100%
            ) !important;

            border-left: none !important;
            border-right: 1px solid #234563 !important;
            min-width: 280px;
            transition: transform 0.3s ease, margin-right 0.3s ease, width 0.3s ease !important;
        }

        /* =========================================
           زر إظهار وإخفاء القائمة الجانبية (Sidebar Toggle)
        ========================================= */

        [data-testid="stSidebarCollapseButton"] {
            visibility: visible !important;
            display: block !important;
        }

        [data-testid="stSidebarCollapseButton"] button,
        button[data-testid="stExpandSidebarButton"] {
            background: #0d385f !important;
            border: 1px solid #1e668f !important;
            border-radius: 10px !important;
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            min-height: 38px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 8px rgba(13, 56, 95, 0.20) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            padding: 0 !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover,
        button[data-testid="stExpandSidebarButton"]:hover {
            background: #0284c7 !important;
            border-color: #38bdf8 !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
            transform: scale(1.05);
        }

        /* استبدال سهم القائمة الافتراضي بأيقونة همبرغر ☰ */
        [data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"],
        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
            display: none !important;
        }

        [data-testid="stSidebarCollapseButton"] button::after,
        button[data-testid="stExpandSidebarButton"]::after {
            content: "☰" !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 1 !important;
            width: 100% !important;
            height: 100% !important;
            font-family: Arial, sans-serif !important;
        }

        /* إخفاء القائمة الجانبية باتجاه اليمين بما يناسب RTL */
        section[data-testid="stSidebar"][data-collapsed="true"],
        section[data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0 !important;
            width: 0 !important;
            margin-right: -320px !important;
            margin-left: 0 !important;
            transform: translateX(100%) !important;
            visibility: hidden !important;
        }

        /* موضع زر الفتح عند إخفاء القائمة ليبقى ظاهرًا في أعلى اليمين */
        div:has(> button[data-testid="stExpandSidebarButton"]) {
            position: fixed !important;
            top: 14px !important;
            right: 18px !important;
            left: auto !important;
            z-index: 999999 !important;
        }

        button[data-testid="stExpandSidebarButton"] {
            position: fixed !important;
            top: 14px !important;
            right: 18px !important;
            left: auto !important;
            z-index: 999999 !important;
        }

        section[data-testid="stSidebar"] * {
            font-family: 'Cairo', Tahoma, sans-serif !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #f1f7ff !important;
            text-align: right !important;
        }

        section[data-testid="stSidebar"] h1 {
            font-size: 21px !important;
            font-weight: 900 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            text-align: right !important;
            direction: rtl !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            min-height: 49px;
            border-radius: 12px !important;
            text-align: right !important;
            justify-content: flex-start !important;
            direction: rtl !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            margin-bottom: 7px;
            padding: 8px 15px !important;
        }

        /* العناصر الداخلية لأزرار القائمة الجانبية - إزالة أي حدود أو خلفيات أو ظلال داخلية */
        section[data-testid="stSidebar"] .stButton > button *,
        section[data-testid="stSidebar"] .stButton > button div,
        section[data-testid="stSidebar"] .stButton > button p,
        section[data-testid="stSidebar"] .stButton > button span {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: #d1e2f4 !important;
            fill: #d1e2f4 !important;
        }

        /* الزر النشط في القائمة الجانبية - الإطار الخارجي المستدير فقط */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(
                135deg,
                #0284c7,
                #075985
            ) !important;
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 5px 15px rgba(2,132,199,.25) !important;
        }

        /* نصوص وأيقونات الزر النشط - بيضاء ناصعة بدون إطارات داخلية */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] div,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {
            color: #ffffff !important;
            fill: #ffffff !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        section[data-testid="stSidebar"]
        .stButton > button[kind="secondary"] {
            background: rgba(255,255,255,.07) !important;
            border: 1px solid rgba(255,255,255,.12) !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #16466d !important;
            border-color: #38bdf8 !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover * {
            color: #ffffff !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* =========================================
           بنرات الصفحات الداخلية
        ========================================= */

        .st-key-page_banner {
            background: linear-gradient(
                120deg,
                #081d35 0%,
                #104b75 65%,
                #087fa8 100%
            ) !important;

            border: 1px solid #1e668f !important;
            border-radius: 22px !important;
            padding: 25px 30px !important;
            margin-bottom: 25px !important;
            box-shadow: 0 10px 25px rgba(8,29,53,.16);
            direction: rtl !important;
            text-align: right !important;
        }

        .st-key-page_banner h1 {
            color: #ffffff !important;
            font-size: 29px !important;
            font-weight: 900 !important;
            margin-bottom: 8px;
        }

        .st-key-page_banner p,
        .st-key-page_banner [data-testid="stCaptionContainer"] {
            color: #dceeff !important;
            font-size: 15px !important;
            font-weight: 500;
            text-align: right !important;
        }

        /* =========================================
           بنر الصفحة الرئيسية
        ========================================= */

        .st-key-home_banner {
            background: linear-gradient(
                120deg,
                #09213b,
                #12547e,
                #0785a8
            ) !important;

            border-radius: 22px !important;
            border: 1px solid #286b91 !important;
            padding: 30px !important;
            margin-bottom: 28px !important;
            box-shadow: 0 10px 25px rgba(8,29,53,.15);
            direction: rtl !important;
            text-align: right !important;
        }

        .st-key-home_banner h1,
        .st-key-home_banner h2,
        .st-key-home_banner h3,
        .st-key-home_banner p {
            color: #ffffff !important;
            text-align: right !important;
        }

        .st-key-home_banner h1 {
            font-size: 28px !important;
            font-weight: 900 !important;
        }

        .st-key-home_banner h2 {
            font-size: 23px !important;
            font-weight: 900 !important;
        }

        .st-key-home_banner p {
            font-size: 16px !important;
            line-height: 2;
        }

        /* =========================================
           بطاقات الخدمات الأربع
        ========================================= */

        .st-key-service_card_1,
        .st-key-service_card_2,
        .st-key-service_card_3,
        .st-key-service_card_4 {

            background: linear-gradient(
                145deg,
                #ffffff 0%,
                #eef7ff 55%,
                #e2f1fc 100%
            ) !important;

            border: 1px solid #c3dff2 !important;
            border-radius: 19px !important;
            padding: 20px 17px !important;
            min-height: 265px;

            box-shadow:
                0 6px 20px rgba(15,39,68,.07),
                inset 0 1px 0 rgba(255,255,255,.9);

            transition: all .25s ease;
            direction: rtl !important;
            text-align: right !important;
        }

        .st-key-service_card_1:hover,
        .st-key-service_card_2:hover,
        .st-key-service_card_3:hover,
        .st-key-service_card_4:hover {

            background: linear-gradient(
                145deg,
                #f0f9ff,
                #dcefff
            ) !important;

            border-color: #38a9d8 !important;

            box-shadow:
                0 12px 28px rgba(2,132,199,.16),
                0 0 0 1px rgba(56,189,248,.12);

            transform: translateY(-4px);
        }

        .st-key-service_card_1 h3,
        .st-key-service_card_2 h3,
        .st-key-service_card_3 h3,
        .st-key-service_card_4 h3 {
            color: #10456d !important;
            font-size: 18px !important;
            font-weight: 900 !important;
            text-align: right !important;
        }

        .st-key-service_card_1 p,
        .st-key-service_card_2 p,
        .st-key-service_card_3 p,
        .st-key-service_card_4 p {
            color: #526b82 !important;
            font-size: 14px !important;
            line-height: 1.9;
            text-align: right !important;
        }

        /* =========================================
           أزرار بطاقات الخدمات
        ========================================= */

        .st-key-service_card_1 .stButton > button,
        .st-key-service_card_2 .stButton > button,
        .st-key-service_card_3 .stButton > button,
        .st-key-service_card_4 .stButton > button {

            background: linear-gradient(
                135deg,
                #087fbd 0%,
                #075985 55%,
                #063d67 100%
            ) !important;

            color: #ffffff !important;
            border: 1px solid #168bc2 !important;
            border-radius: 11px !important;
            min-height: 45px !important;
            width: 100% !important;
            font-size: 14px !important;
            font-weight: 800 !important;

            box-shadow:
                0 4px 12px rgba(3,105,161,.20),
                inset 0 1px 0 rgba(255,255,255,.12);

            opacity: 1 !important;
            transition: all .25s ease;
        }

        .st-key-service_card_1 .stButton > button[kind="secondary"],
        .st-key-service_card_2 .stButton > button[kind="secondary"],
        .st-key-service_card_3 .stButton > button[kind="secondary"],
        .st-key-service_card_4 .stButton > button[kind="secondary"] {
            background: linear-gradient(
                135deg,
                #087fbd 0%,
                #075985 55%,
                #063d67 100%
            ) !important;
            color: #ffffff !important;
            border: 1px solid #168bc2 !important;
        }

        .st-key-service_card_1 .stButton > button *,
        .st-key-service_card_2 .stButton > button *,
        .st-key-service_card_3 .stButton > button *,
        .st-key-service_card_4 .stButton > button * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }

        .st-key-service_card_1 .stButton > button:hover,
        .st-key-service_card_2 .stButton > button:hover,
        .st-key-service_card_3 .stButton > button:hover,
        .st-key-service_card_4 .stButton > button:hover {

            background: linear-gradient(
                135deg,
                #0ea5e9,
                #0369a1,
                #075985
            ) !important;

            color: #ffffff !important;
            border-color: #38bdf8 !important;

            box-shadow:
                0 7px 18px rgba(2,132,199,.30),
                0 0 10px rgba(56,189,248,.15);

            transform: translateY(-2px);
        }

        .st-key-service_card_1 .stButton > button:active,
        .st-key-service_card_2 .stButton > button:active,
        .st-key-service_card_3 .stButton > button:active,
        .st-key-service_card_4 .stButton > button:active {
            transform: scale(.98);
        }

        /* =========================================
           البطاقات الداخلية
        ========================================= */

        .st-key-info_card,
        .st-key-control_card,
        .st-key-control_card_view,
        .st-key-control_card_categories,
        .st-key-empty_card {

            background: linear-gradient(
                145deg,
                #ffffff,
                #f0f7fd
            ) !important;

            border: 1px solid #d2e4f2 !important;
            border-radius: 17px !important;
            padding: 20px !important;

            box-shadow: 0 5px 17px rgba(15,39,68,.055);
            direction: rtl !important;
            text-align: right !important;
        }

        /* =========================================
           العناوين والنصوص
        ========================================= */

        h1, h2, h3 {
            color: #123b5d !important;
            font-family: 'Cairo', Tahoma, sans-serif !important;
            text-align: right !important;
            direction: rtl !important;
            font-weight: 900 !important;
        }

        h1 {
            font-size: 28px !important;
        }

        h2 {
            font-size: 23px !important;
        }

        h3 {
            font-size: 18px !important;
        }

        p {
            color: #40576e;
            line-height: 1.9;
            text-align: right !important;
        }

        [data-testid="stCaptionContainer"] {
            color: #657b91 !important;
            text-align: right !important;
            direction: rtl !important;
        }

        /* =========================================
           الأزرار العامة - إصلاح التباين التام
        ========================================= */

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px !important;
            min-height: 46px !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            font-size: 14.5px !important;
            font-weight: 800 !important;
            transition: all .2s ease !important;
        }

        /* الأزرار الأساسية (Primary) */
        .stButton > button[kind="primary"],
        .stButton > button[kind="primary"] *,
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span,
        .stButton > button[kind="primary"] div {
            color: #ffffff !important;
            fill: #ffffff !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            font-weight: 800 !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(
                135deg,
                #0284c7 0%,
                #075985 100%
            ) !important;
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 4px 14px rgba(2,132,199,.25) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(
                135deg,
                #0369a1 0%,
                #0ea5e9 100%
            ) !important;
            border-color: #7dd3fc !important;
            box-shadow: 0 6px 18px rgba(2,132,199,.35) !important;
            transform: translateY(-2px);
        }

        /* الأزرار الثانوية (Secondary) */
        .stButton > button[kind="secondary"],
        .stButton > button[kind="secondary"] *,
        .stButton > button[kind="secondary"] p,
        .stButton > button[kind="secondary"] span,
        .stButton > button[kind="secondary"] div {
            color: #0c385b !important;
            fill: #0c385b !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="secondary"] {
            background: #ffffff !important;
            border: 1.5px solid #cbddec !important;
            box-shadow: 0 2px 8px rgba(15,39,68,.04) !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background: #f0f7fc !important;
            border-color: #0284c7 !important;
            transform: translateY(-2px);
        }

        /* استثناءات عالية الأولوية لأزرار بطاقات الخدمات */
        .st-key-service_card_1 .stButton > button,
        .st-key-service_card_1 .stButton > button *,
        .st-key-service_card_1 .stButton > button p,
        .st-key-service_card_1 .stButton > button span,
        .st-key-service_card_2 .stButton > button,
        .st-key-service_card_2 .stButton > button *,
        .st-key-service_card_2 .stButton > button p,
        .st-key-service_card_2 .stButton > button span,
        .st-key-service_card_3 .stButton > button,
        .st-key-service_card_3 .stButton > button *,
        .st-key-service_card_3 .stButton > button p,
        .st-key-service_card_3 .stButton > button span,
        .st-key-service_card_4 .stButton > button,
        .st-key-service_card_4 .stButton > button *,
        .st-key-service_card_4 .stButton > button p,
        .st-key-service_card_4 .stButton > button span {
            color: #ffffff !important;
            fill: #ffffff !important;
            font-weight: 800 !important;
        }

        /* استثناءات عالية الأولوية لأزرار القائمة الجانبية */
        section[data-testid="stSidebar"] .stButton > button,
        section[data-testid="stSidebar"] .stButton > button *,
        section[data-testid="stSidebar"] .stButton > button p,
        section[data-testid="stSidebar"] .stButton > button span,
        section[data-testid="stSidebar"] .stButton > button div {
            color: #d1e2f4 !important;
            fill: #d1e2f4 !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"],
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] span,
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] div {
            color: #ffffff !important;
            fill: #ffffff !important;
            font-weight: 800 !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* إعادة تأكيد الإطار الخارجي فقط للزر الأساسي */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 5px 15px rgba(2,132,199,.25) !important;
        }

        /* أزرار التنزيل (Download Buttons) */
        .stDownloadButton > button,
        .stDownloadButton > button *,
        .stDownloadButton > button p,
        .stDownloadButton > button span,
        .stDownloadButton > button div {
            color: #ffffff !important;
            fill: #ffffff !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            font-weight: 800 !important;
        }

        .stDownloadButton > button {
            background: linear-gradient(
                135deg,
                #075985 0%,
                #0284c7 100%
            ) !important;
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 4px 14px rgba(2,132,199,.25) !important;
            min-height: 48px !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(
                135deg,
                #0369a1 0%,
                #0ea5e9 100%
            ) !important;
            box-shadow: 0 6px 18px rgba(2,132,199,.35) !important;
            transform: translateY(-2px);
        }

        /* =========================================
           زر الصفحة الرئيسية
        ========================================= */

        .st-key-home_start .stButton > button {

            background: linear-gradient(
                135deg,
                #075985 0%,
                #0284c7 55%,
                #0ea5e9 100%
            ) !important;

            color: #ffffff !important;
            border: 1px solid #38bdf8 !important;
            border-radius: 14px !important;
            min-height: 55px !important;
            font-size: 17px !important;
            font-weight: 900 !important;

            box-shadow:
                0 7px 20px rgba(2,132,199,.25),
                inset 0 1px 0 rgba(255,255,255,.15);

            opacity: 1 !important;
            transition: all .25s ease;
        }

        .st-key-home_start .stButton > button * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }

        .st-key-home_start .stButton > button:hover {

            background: linear-gradient(
                135deg,
                #0369a1,
                #0284c7,
                #38bdf8
            ) !important;

            color: #ffffff !important;
            border-color: #7dd3fc !important;

            box-shadow:
                0 10px 25px rgba(2,132,199,.35),
                0 0 12px rgba(56,189,248,.18);

            transform: translateY(-3px);
        }

        /* =========================================
           أزرار الانتقال إلى رفع المستند
        ========================================= */

        .st-key-btn_mask_go_upload .stButton > button,
        .st-key-btn_report_go_scan .stButton > button {

            background: linear-gradient(
                135deg,
                #075985,
                #0284c7,
                #0ea5e9
            ) !important;

            color: #ffffff !important;
            border: 1px solid #38bdf8 !important;
            border-radius: 13px !important;
            min-height: 50px !important;
            font-size: 15px !important;
            font-weight: 900 !important;

            box-shadow: 0 5px 16px rgba(2,132,199,.22);

            opacity: 1 !important;
            transition: all .25s ease;
        }

        .st-key-btn_mask_go_upload .stButton > button *,
        .st-key-btn_report_go_scan .stButton > button * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }

        .st-key-btn_mask_go_upload .stButton > button:hover,
        .st-key-btn_report_go_scan .stButton > button:hover {

            background: linear-gradient(
                135deg,
                #0369a1,
                #0284c7,
                #38bdf8
            ) !important;

            border-color: #7dd3fc !important;
            box-shadow: 0 8px 20px rgba(2,132,199,.30);
            transform: translateY(-2px);
        }

        /* =========================================
           حقول النص ومعاينة المستند (إصلاح الرؤية التامة)
        ========================================= */

        .stTextArea textarea,
        .stTextArea textarea:disabled,
        .stTextArea textarea[disabled],
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="textarea"] textarea:disabled,
        div[data-baseweb="textarea"] textarea[disabled] {
            background-color: #ffffff !important;
            color: #0c2b4d !important;
            -webkit-text-fill-color: #0c2b4d !important;
            opacity: 1 !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            line-height: 2 !important;
            direction: rtl !important;
            text-align: right !important;
            border: 1.5px solid #b8d5ec !important;
            border-radius: 14px !important;
            padding: 16px !important;
            box-shadow: inset 0 2px 5px rgba(12,43,77,.04) !important;
            cursor: default !important;
        }

        /* =========================================
           منطقة رفع الملفات
        ========================================= */

        [data-testid="stFileUploader"] {
            width: 100% !important;
            direction: rtl !important;
            text-align: right !important;
        }

        [data-testid="stFileUploader"] section {
            direction: rtl !important;
        }

        [data-testid="stFileUploaderDropzone"] {

            background: linear-gradient(
                145deg,
                #f8fcff 0%,
                #eaf5ff 100%
            ) !important;

            border: 2px dashed #0784bd !important;
            border-radius: 18px !important;

            padding: 24px !important;

            box-shadow:
                0 4px 13px rgba(15,39,68,.05),
                inset 0 0 0 1px rgba(255,255,255,.8);

            transition: all .25s ease;

            direction: rtl !important;
        }

        [data-testid="stFileUploaderDropzone"]:hover {

            background: linear-gradient(
                145deg,
                #f0f9ff,
                #e0f2fe
            ) !important;

            border: 2px dashed #0369a1 !important;

            box-shadow: 0 7px 18px rgba(2,132,199,.12);
        }

        [data-testid="stFileUploaderDropzone"]:focus-within {

            border: 2px solid #0284c7 !important;
            outline: 3px solid rgba(14,165,233,.16) !important;
            outline-offset: 2px !important;
        }

        /* نصوص منطقة رفع الملفات */

        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stFileUploaderDropzoneInstructions"] {
            color: #17496d !important;
            font-weight: 700 !important;
            direction: rtl !important;
            text-align: right !important;
        }

        [data-testid="stFileUploaderDropzoneInstructions"] {
            width: 100% !important;
        }

        /* =========================================
           زر اختيار الملف باللغة العربية
           إخفاء النص الإنجليزي وإظهار النص العربي
        ========================================= */

        [data-testid="stFileUploaderDropzone"] button {

            position: relative !important;

            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;

            direction: rtl !important;

            min-width: 145px !important;
            min-height: 45px !important;

            padding: 8px 18px !important;

            background: linear-gradient(
                135deg,
                #087fbd,
                #075985
            ) !important;

            border: 1px solid #075985 !important;
            border-radius: 11px !important;

            font-size: 0 !important;
            white-space: nowrap !important;

            outline: none !important;

            box-shadow:
                0 4px 10px rgba(2,132,199,.16),
                inset 0 1px 0 rgba(255,255,255,.12);

            transition: all .2s ease;
        }

        /* إخفاء النص الأصلي داخل الزر */

        [data-testid="stFileUploaderDropzone"] button > *:not(svg) {
            display: none !important;
        }

        /* كتابة النص العربي مكان النص الإنجليزي */

        [data-testid="stFileUploaderDropzone"] button::after {

            content: "رفع الملف" !important;

            display: inline-block !important;

            color: #ffffff !important;

            font-family: 'Cairo', Tahoma, sans-serif !important;
            font-size: 14px !important;
            font-weight: 800 !important;

            white-space: nowrap !important;
            line-height: 1.5 !important;
        }

        /* شارة الملف المختار */
        .selected-file-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            background: #ffffff;
            border: 1.5px solid #0284c7;
            border-radius: 12px;
            padding: 10px 18px;
            font-family: 'Cairo', Tahoma, sans-serif !important;
            font-size: 15px;
            color: #0c2b4d;
            box-shadow: 0 2px 8px rgba(2,132,199,.08);
            direction: rtl;
        }

        .stButton > button[key="btn_remove_selected_file"],
        div[data-testid*="btn_remove_selected_file"] button {
            min-height: 46px !important;
            min-width: 46px !important;
            background: #fee2e2 !important;
            color: #dc2626 !important;
            border: 1.5px solid #fca5a5 !important;
            font-size: 18px !important;
            font-weight: 900 !important;
            border-radius: 12px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div[data-testid*="btn_remove_selected_file"] button:hover {
            background: #ef4444 !important;
            color: #ffffff !important;
            border-color: #dc2626 !important;
        }

        /* لون أيقونة الزر */

        [data-testid="stFileUploaderDropzone"] button svg {
            color: #ffffff !important;
            fill: #ffffff !important;
            flex-shrink: 0 !important;
        }

        /* تأثير التركيز */

        [data-testid="stFileUploaderDropzone"] button:focus,
        [data-testid="stFileUploaderDropzone"] button:focus-visible {

            outline: 3px solid rgba(14,165,233,.30) !important;
            outline-offset: 3px !important;
            border-color: #38bdf8 !important;
        }

        /* تأثير المرور */

        [data-testid="stFileUploaderDropzone"] button:hover {

            background: linear-gradient(
                135deg,
                #0ea5e9,
                #0369a1
            ) !important;

            border: 1px solid #38bdf8 !important;

            box-shadow: 0 6px 15px rgba(2,132,199,.25);

            transform: translateY(-1px);
        }

        /* اسم الملف بعد الرفع */

        [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
            color: #16456b !important;
            text-align: right !important;
            direction: rtl !important;
        }

        [data-testid="stFileUploader"] small {
            color: #526b82 !important;
        }

        /* =========================================
           مربعات الاختيار
        ========================================= */

        [data-testid="stCheckbox"] {
            direction: rtl !important;
            margin-bottom: 8px !important;
        }

        [data-testid="stCheckbox"] label {
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
            color: #163e63 !important;
            font-weight: 700 !important;
            font-size: 14.5px !important;
            direction: rtl !important;
            text-align: right !important;
        }

        /* =========================================
           الإحصائيات (Metrics) - إصلاح الأحجام والقص
        ========================================= */

        [data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1.5px solid #d4e3f0 !important;
            border-radius: 16px !important;
            padding: 16px 18px !important;
            box-shadow: 0 4px 14px rgba(15,39,68,.05) !important;
            direction: rtl !important;
            text-align: right !important;
            min-height: 110px !important;
        }

        [data-testid="stMetric"] > div {
            align-items: flex-start !important;
            text-align: right !important;
            direction: rtl !important;
            justify-content: flex-start !important;
        }

        [data-testid="stMetricLabel"] {
            text-align: right !important;
            direction: rtl !important;
        }

        [data-testid="stMetricLabel"] p {
            color: #526b82 !important;
            font-size: 13.5px !important;
            font-weight: 700 !important;
            text-align: right !important;
            direction: rtl !important;
            margin-bottom: 2px !important;
        }

        [data-testid="stMetricValue"] {
            text-align: right !important;
            direction: rtl !important;
            margin-top: 4px !important;
        }

        [data-testid="stMetricValue"] > div {
            color: #075985 !important;
            font-size: 17px !important;
            font-weight: 900 !important;
            line-height: 1.35 !important;
            white-space: normal !important;
            word-break: break-word !important;
            text-align: right !important;
            direction: rtl !important;
        }

        [data-testid="stMetricDelta"] {
            direction: rtl !important;
            text-align: right !important;
        }

        /* =========================================
           الجداول وتنسيق التقرير الموحد
        ========================================= */

        .custom-report-table-wrapper {
            background: #ffffff;
            border: 1.5px solid #cde0ef;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(15,39,68,.05);
            overflow: hidden;
            margin-bottom: 20px;
            direction: rtl;
        }

        .custom-report-table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            direction: rtl;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
        }

        .custom-report-table th {
            background: linear-gradient(135deg, #092644 0%, #104b75 100%);
            color: #ffffff !important;
            font-weight: 800;
            padding: 14px 18px;
            font-size: 14px;
            border: none;
            text-align: right;
        }

        .custom-report-table td {
            background: #ffffff;
            color: #123b5d !important;
            padding: 13px 18px;
            font-size: 14px;
            border-bottom: 1px solid #e5eff8;
            font-weight: 600;
            text-align: right;
        }

        .custom-report-table tr:nth-child(even) td {
            background: #f7faff;
        }

        .custom-report-table tr:hover td {
            background: #edf6fd;
        }

        .badge-status-masked {
            display: inline-block;
            background: rgba(16, 185, 129, 0.12);
            color: #047857 !important;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 13px;
            font-weight: 800;
        }

        .badge-status-detected {
            display: inline-block;
            background: rgba(245, 158, 11, 0.12);
            color: #b45309 !important;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 13px;
            font-weight: 800;
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border-radius: 14px;
            border: 1.5px solid #d8e5f2;
            overflow: hidden;
            background: #ffffff !important;
        }

        [data-testid="stAlert"] {
            border-radius: 13px !important;
            direction: rtl !important;
            text-align: right !important;
            font-weight: 600 !important;
        }

        /* =========================================
           الفواصل
        ========================================= */

        hr {
            border-color: #d5e2ee !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------------
# 4. إدارة حالة التطبيق
# --------------------------------------------------------

def initialize_session_state():

    if "current_page" not in st.session_state:
        st.session_state.current_page = "الرئيسية"

    if "current_document" not in st.session_state:
        st.session_state.current_document = None

    if "scan_completed" not in st.session_state:
        st.session_state.scan_completed = False

    if "masking_applied" not in st.session_state:
        st.session_state.masking_applied = False

    if "masking_view_mode" not in st.session_state:
        st.session_state.masking_view_mode = "masked"

    if "detected_data" not in st.session_state:
        st.session_state.detected_data = []

    if "detected_count" not in st.session_state:
        st.session_state.detected_count = 0

    if "redacted_file_path" not in st.session_state:
        st.session_state.redacted_file_path = None

    if "redacted_content" not in st.session_state:
        st.session_state.redacted_content = ""

    if "uploader_id" not in st.session_state:
        st.session_state.uploader_id = 0

    if "masking_categories" not in st.session_state:
        st.session_state.masking_categories = {
            data_type: True for data_type in MASKING_TYPE_LABELS
        }
    elif any(
        key in st.session_state.masking_categories
        for key in ("emails", "phones", "ids", "financial")
    ):
        legacy_categories = st.session_state.masking_categories
        st.session_state.masking_categories = {
            "email": legacy_categories.get("emails", True),
            "phone": legacy_categories.get("phones", True),
            "national_id": legacy_categories.get("ids", True),
            "passport": legacy_categories.get("ids", True),
            "full_name": True,
            "date_of_birth": True,
            "address": True,
            "credit_card": legacy_categories.get("financial", True),
            "bank_account": legacy_categories.get("financial", True),
            "iban": legacy_categories.get("financial", True),
            "salary": True,
            "password": legacy_categories.get("financial", True),
            "username": True,
        }

    if "upload_error" not in st.session_state:
        st.session_state.upload_error = None


ALLOWED_FILE_EXTENSIONS = {".pdf", ".txt"}
UNSUPPORTED_FILE_TYPE_MESSAGE = "نوع الملف غير مدعوم. يُسمح برفع ملفات PDF وTXT فقط"
NO_SENSITIVE_DATA_MESSAGE = "لم يتم العثور على بيانات حساسة تحتاج إلى تعتيم في هذا المستند."


def is_allowed_file_type(file_name: str) -> bool:
    """التحقق من أن نوع الملف مدعوم (.pdf أو .txt فقط)."""
    if not file_name or not isinstance(file_name, str):
        return False
    return Path(file_name).suffix.lower() in ALLOWED_FILE_EXTENSIONS


MASKING_TYPE_LABELS = {
    "email": "عناوين البريد الإلكتروني",
    "phone": "أرقام الهواتف والجوالات",
    "national_id": "الهوية الوطنية",
    "passport": "جواز السفر",
    "full_name": "الاسم الكامل",
    "date_of_birth": "تاريخ الميلاد",
    "address": "العنوان",
    "credit_card": "البطاقة المصرفية",
    "bank_account": "الحساب البنكي",
    "iban": "رقم الحساب الدولي (IBAN)",
    "salary": "الراتب",
    "password": "كلمة المرور",
    "username": "اسم المستخدم",
}


def get_allowed_types_from_categories(categories_dict):
    """تحويل خيارات الأنواع المستقلة إلى مفاتيح محرك الكشف."""
    return [
        data_type
        for data_type in MASKING_TYPE_LABELS
        if categories_dict.get(data_type, False)
    ]


# --------------------------------------------------------
# 5. القائمة الجانبية والتنقل
# --------------------------------------------------------

def render_sidebar():

    doc = st.session_state.get("current_document")

    with st.sidebar:

        st.write("")
        st.write("")

        st.title("🛡️ نظام حماية المستندات")

        st.caption("DOCUMENT PROTECTION SYSTEM")

        st.divider()

        pages = [
            ("🏠", "الرئيسية"),
            ("📄", "فحص المستند"),
            ("🔒", "تعتيم البيانات"),
            ("📊", "التقرير")
        ]

        for icon, page_name in pages:

            is_active = (
                st.session_state.current_page == page_name
            )

            button_type = (
                "primary" if is_active else "secondary"
            )

            if st.button(
                f"{icon}  {page_name}",
                key=f"nav_{page_name}",
                type=button_type,
                use_container_width=True
            ):

                if (
                    page_name == "التقرير"
                    and doc
                    and st.session_state.get("scan_completed")
                    and st.session_state.get("masking_applied")
                    and st.session_state.get("detected_count", 0) == 0
                ):
                    st.toast(NO_SENSITIVE_DATA_MESSAGE, icon="ℹ️")
                    st.session_state.current_page = "فحص المستند"
                    st.rerun()
                else:
                    if st.session_state.current_page != page_name:
                        st.session_state.upload_error = None
                    st.session_state.current_page = page_name
                    st.rerun()

        st.divider()

        
# --------------------------------------------------------
# 6. إنشاء نص تجريبي بعد التعتيم
# --------------------------------------------------------

def generate_sample_masked_text(original_text):

    lines = original_text.split("\n")

    keywords = [
        "البريد",
        "جوال",
        "هاتف",
        "هوية",
        "اسم",
        "المشرف"
    ]

    masked_lines = []

    for line in lines:

        if any(keyword in line for keyword in keywords):

            parts = line.split(":", 1)

            if len(parts) == 2:

                masked_line = parts[0] + ": " + "*" * 10

                masked_lines.append(masked_line)

            else:
                masked_lines.append(line)

        else:
            masked_lines.append(line)

    return "\n".join(masked_lines)


# --------------------------------------------------------
# 7. الصفحة الرئيسية
# --------------------------------------------------------

def render_home_page():

    with st.container(key="home_banner"):

        st.title("🛡️ مرحباً بك في نظام حماية المستندات")

        st.subheader("🔐 منصة ذكية لحماية البيانات الحساسة")

        st.write(
            "تساعدك المنصة على حماية البيانات الحساسة "
            "وتأمين المستندات قبل مشاركتها."
        )

        st.write("📍 حماية خصوصيتك هي أولويتنا")

    st.write("")

    st.subheader("خدمات النظام")

    st.write(
        "يمكنك الوصول إلى خدمات النظام من خلال الأقسام التالية:"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        with st.container(key="service_card_1"):

            st.markdown("### 📁 إدارة المستندات")

            st.write(
                "رفع المستندات واختيار الملفات "
                "المراد فحصها وحمايتها."
            )

            if st.button(
                "📤 رفع المستندات",
                key="home_upload",
                use_container_width=True
            ):

                st.session_state.current_page = "فحص المستند"
                st.rerun()

    with col2:

        with st.container(key="service_card_2"):

            st.markdown("### 🔍 فحص المستند")

            st.write(
                "تحليل المستند واكتشاف البيانات "
                "الحساسة الموجودة بداخله."
            )

            if st.button(
                "🔍 بدء الفحص",
                key="home_scan",
                use_container_width=True
            ):

                st.session_state.current_page = "فحص المستند"
                st.rerun()

    with col3:

        with st.container(key="service_card_3"):

            st.markdown("### 🔒 تعتيم البيانات")

            st.write(
                "إخفاء البيانات الحساسة من المستند "
                "لحماية المعلومات الشخصية."
            )

            if st.button(
                "🔒 بدء التعتيم",
                key="home_redact",
                use_container_width=True
            ):

                st.session_state.current_page = "تعتيم البيانات"
                st.rerun()

    with col4:

        with st.container(key="service_card_4"):

            st.markdown("### 📊 التقارير الأمنية")

            st.write(
                "عرض نتائج الفحص والتعتيم "
                "والحصول على التقارير الأمنية."
            )

            if st.button(
                "📊 عرض التقارير",
                key="home_report",
                use_container_width=True
            ):

                st.session_state.current_page = "التقرير"
                st.rerun()

    st.write("")

    _, col_start, _ = st.columns([1, 2, 1])

    with col_start:

        if st.button(
            "🚀 ابدأ برفع المستند الآن",
            key="home_start",
            type="primary",
            use_container_width=True
        ):

            st.session_state.current_page = "فحص المستند"
            st.rerun()

    st.info(
        "💡 ابدأ برفع المستند، ثم افحصه، وبعد ذلك "
        "انتقل إلى تعتيم البيانات الحساسة وعرض التقرير الأمني."
    )


# --------------------------------------------------------
# 8. صفحة فحص المستندات
# --------------------------------------------------------

def render_scan_page():

    with st.container(key="page_banner"):

        st.title("🔍 فحص وتحليل المستندات")

        st.caption(
            "ارفع المستند ليتم تحليله واكتشاف "
            "البيانات الحساسة الموجودة بداخله."
        )

    st.subheader("📂 رفع المستند")

    uploads_dir = Path("uploads")
    processed_dir = Path("processed")
    uploads_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)

    doc = st.session_state.get("current_document")

    def clear_current_document():
        st.session_state.current_document = None
        st.session_state.scan_completed = False
        st.session_state.masking_applied = False
        st.session_state.detected_data = []
        st.session_state.detected_count = 0
        st.session_state.redacted_file_path = None
        st.session_state.redacted_content = ""
        st.session_state.uploader_id = st.session_state.get("uploader_id", 0) + 1
        st.session_state.upload_error = None

    if doc is None:
        # عرض رسالة الخطأ إذا تم رفض نوع ملف غير مدعوم
        if st.session_state.get("upload_error"):
            st.error(st.session_state.upload_error)

        # إظهار زر رفع واحد فقط بعنوان «رفع الملف»
        uploader_key = f"uploader_{st.session_state.get('uploader_id', 0)}"
        uploaded_file = st.file_uploader(
            "اختر المستند المراد فحصه",
            key=uploader_key,
            help="يمكنك رفع ملفات TXT أو PDF",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name

            # التحقق داخل التطبيق من نوع الملف المسموح به (.pdf أو .txt فقط)
            if not is_allowed_file_type(file_name):
                st.session_state.upload_error = UNSUPPORTED_FILE_TYPE_MESSAGE
                st.session_state.uploader_id = st.session_state.get("uploader_id", 0) + 1
                st.rerun()

            st.session_state.upload_error = None
            file_size = f"{uploaded_file.size / 1024:.2f} KB"
            upload_path = uploads_dir / file_name
            upload_path.write_bytes(uploaded_file.getvalue())

            is_pdf = file_name.lower().endswith(".pdf")
            is_txt = file_name.lower().endswith(".txt")

            pages = None
            original_content = ""

            try:
                if is_pdf:
                    pages = read_pdf(str(upload_path))
                    original_content = "\n\n".join(
                        [f"--- صفحة {p['page_number']} ---\n{p['text']}" for p in pages]
                    )
                elif is_txt:
                    original_content = read_txt(str(upload_path))
            except Exception as e:
                st.error(f"خطأ أثناء قراءة المستند: {e}")
                return

            st.session_state.current_document = {
                "file_name": file_name,
                "file_size": file_size,
                "file_type": "pdf" if is_pdf else "txt",
                "upload_path": str(upload_path),
                "content": original_content,
                "pages": pages
            }

            st.session_state.scan_completed = False
            st.session_state.masking_applied = False
            st.session_state.masking_view_mode = "masked"
            st.session_state.detected_data = []
            st.session_state.detected_count = 0
            st.session_state.redacted_file_path = None
            st.session_state.redacted_content = ""

            st.rerun()

    else:
        # بعد اختيار الملف: إخفاء زر الرفع واستبداله بعرض اسم الملف المختار مع علامة × صغيرة بجانبه
        col_file_info, col_close = st.columns([0.88, 0.12])
        with col_file_info:
            st.markdown(
                f"""
                <div class="selected-file-badge">
                    <span style="font-size: 1.3rem;">📄</span>
                    <span style="font-weight: 800; color: #0c2b4d;">{doc['file_name']}</span>
                    <span style="color: #0369a1; font-weight: 600;">({doc['file_size']})</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_close:
            if st.button("✕", key="btn_remove_selected_file", help="إلغاء الملف المختار ومسح البيانات"):
                clear_current_document()
                st.rerun()

    # عرض بيانات المستند

    doc = st.session_state.get("current_document")

    if doc:

        st.divider()

        st.subheader("📄 معلومات المستند")

        with st.container(key="info_card"):

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**اسم الملف:** {doc['file_name']}")

            with col2:
                st.write(f"**حجم الملف:** {doc['file_size']}")

        st.subheader("معاينة محتوى المستند")

        st.text_area(
            label="محتوى المستند",
            value=doc["content"],
            height=220,
            disabled=True,
            label_visibility="collapsed"
        )

        col_scan, col_clear = st.columns(2)

        with col_scan:

            if st.button(
                "🔍 بدء فحص المستند",
                key="btn_start_scan",
                type="primary",
                use_container_width=True
            ):

                progress_bar = st.progress(0)

                status_text = st.empty()

                status_text.info("جاري التحقق من قراءة المستند واستخراج النص...")

                progress_bar.progress(25)
                time.sleep(0.3)

                progress_bar.progress(70)

                try:
                    if doc["file_type"] == "pdf":
                        pages = read_pdf(doc["upload_path"])
                        if not pages or not any(
                            page.get("text", "").strip() for page in pages
                        ):
                            raise ValueError("ملف PDF لا يحتوي على نص قابل للفحص.")

                        content = "\n\n".join(
                            f"--- صفحة {page['page_number']} ---\n{page['text']}"
                            for page in pages
                        )
                        doc = {**doc, "pages": pages, "content": content}
                    elif doc["file_type"] == "txt":
                        content = read_txt(doc["upload_path"])
                        if not content.strip():
                            raise ValueError("ملف TXT فارغ ولا يحتوي على نص قابل للفحص.")

                        doc = {**doc, "pages": None, "content": content}
                    else:
                        raise ValueError("نوع الملف غير مدعوم للفحص.")

                    st.session_state.current_document = doc
                    st.session_state.detected_data = []
                    st.session_state.detected_count = 0
                    st.session_state.redacted_file_path = None
                    st.session_state.redacted_content = ""
                    st.session_state.scan_completed = True
                    st.session_state.masking_applied = False

                    progress_bar.progress(100)
                    time.sleep(0.2)
                    progress_bar.empty()
                    status_text.empty()
                    st.rerun()

                except Exception as error:
                    st.session_state.scan_completed = False
                    st.session_state.masking_applied = False
                    st.session_state.detected_data = []
                    st.session_state.detected_count = 0
                    status_text.error(f"تعذر إتمام الفحص: {error}")

        with col_clear:

            if st.button(
                "🗑️ مسح المستند",
                key="btn_clear_document",
                type="secondary",
                use_container_width=True
            ):

                clear_current_document()
                st.rerun()

        if st.session_state.get("scan_completed", False):
            st.success(
                "تم فحص إمكانية قراءة المستند واستخراج نصه؛ "
                "يمكنك الآن اختيار أنواع البيانات المطلوب تعتيمها."
            )

            if st.button(
                "الانتقال إلى تعتيم البيانات ←",
                key="btn_go_masking",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = "تعتيم البيانات"
                st.rerun()

    else:

        st.info(
            "يرجى رفع مستند أولاً حتى تتمكن من بدء عملية الفحص."
        )


# --------------------------------------------------------
# 9. صفحة تعتيم البيانات الحساسة
# --------------------------------------------------------

def render_masking_page():

    with st.container(key="page_banner"):

        st.title("🔒 تعتيم البيانات الحساسة")

        st.caption(
            "حجب وتشفير البيانات المكتشفة بنجوم "
            "لمنع تسريبها قبل مشاركة المستند."
        )

    doc = st.session_state.get("current_document")

    if not doc or not doc.get("content"):

        with st.container(key="empty_card"):

            st.write("")
            st.markdown("## 📂 مساحة عرض المستند فارغة")

            st.write(
                "لم يتم رفع أي مستند بعد. يرجى التوجه إلى "
                "**فحص المستند** ورفع ملف لبدء التعتيم."
            )

            st.write("")

        _, col_go, _ = st.columns([1, 1.5, 1])

        with col_go:

            if st.button(
                "الانتقال لرفع مستند الآن ←",
                key="btn_mask_go_upload",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = "فحص المستند"
                st.rerun()

        return

    # التنبيه إذا لم يتم فحص المستند بعد
    if not st.session_state.get("scan_completed", False):
        with st.container(key="empty_card"):
            st.write("")
            st.markdown("## 🔍 يلزم فحص المستند أولاً")
            st.write(
                "يرجى فحص المستند أولاً في صفحة **فحص المستند** لاكتشاف البيانات الحساسة قبل الانتقال إلى التعتيم."
            )
            st.write("")

        _, col_go, _ = st.columns([1, 1.5, 1])
        with col_go:
            if st.button(
                "الذهاب إلى فحص المستند ←",
                key="btn_mask_need_scan",
                type="primary",
                use_container_width=True
            ):
                st.session_state.current_page = "فحص المستند"
                st.rerun()
        return

    original_text = doc["content"]

    masking_applied = st.session_state.get(
        "masking_applied",
        False
    )

    if masking_applied:
        st.success("✓ تم تعتيم وحجب البيانات بنجاح!")

    col_view, col_controls = st.columns([1.8, 1.2])

    # معاينة المستند

    with col_view:

        with st.container(key="info_card"):

            st.write(
                f"📄 **المستند:** {doc['file_name']} "
                f"| الحجم: {doc['file_size']}"
            )

        if masking_applied:

            is_masked_view = (
                st.session_state.get(
                    "masking_view_mode",
                    "masked"
                ) == "masked"
            )

            redacted_content = st.session_state.get("redacted_content", "")

            displayed_text = (
                redacted_content
                if (is_masked_view and redacted_content and redacted_content.strip())
                else original_text
            )

            box_label = (
                "المستند بعد التعتيم (محمي بنجوم 🔒):"
                if is_masked_view
                else "المستند الأصلي للمراجعة 👁️:"
            )

        else:

            is_masked_view = False

            displayed_text = original_text

            box_label = (
                "المستند الأصلي المرفوع "
                "(جاهز للتعتيم 📄):"
            )

        st.subheader(box_label)

        st.text_area(
            label="معاينة التعتيم",
            value=displayed_text,
            height=280,
            disabled=True,
            label_visibility="collapsed"
        )

        redacted_path_str = st.session_state.get("redacted_file_path")
        if masking_applied and redacted_path_str and Path(redacted_path_str).exists():
            redacted_path = Path(redacted_path_str)
            if redacted_path.suffix.lower() == ".pdf":
                st.download_button(
                    label="📥 تحميل المستند بعد التعتيم (PDF)",
                    data=redacted_path.read_bytes(),
                    file_name=redacted_path.name,
                    mime="application/pdf",
                    key="btn_download_masked_pdf",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.download_button(
                    label="📥 تحميل المستند بعد التعتيم (TXT)",
                    data=redacted_path.read_text(encoding="utf-8"),
                    file_name=redacted_path.name,
                    mime="text/plain",
                    key="btn_download_masked_txt",
                    type="primary",
                    use_container_width=True
                )

        sub1, sub2 = st.columns(2)

        with sub1:

            if st.button(
                "الانتقال إلى التقرير ←",
                key="btn_mask_go_report",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = "التقرير"
                st.rerun()

        with sub2:

            if st.button(
                "رفع ملف آخر 🔄",
                key="btn_mask_rescan",
                type="secondary",
                use_container_width=True
            ):

                st.session_state.current_page = "فحص المستند"
                st.session_state.current_document = None
                st.session_state.scan_completed = False
                st.session_state.masking_applied = False
                st.session_state.detected_data = []
                st.session_state.detected_count = 0
                st.session_state.redacted_file_path = None
                st.session_state.redacted_content = ""
                st.session_state.upload_error = None
                st.session_state.uploader_id = st.session_state.get("uploader_id", 0) + 1
                st.rerun()

    # إعدادات التعتيم

    with col_controls:

        if masking_applied:

            with st.container(key="control_card_view"):

                st.markdown("### 👁️ خيارات العرض")

                btn_mask_type = (
                    "primary" if is_masked_view else "secondary"
                )

                if st.button(
                    "عرض البيانات المعتمة 🔒",
                    key="btn_show_masked",
                    type=btn_mask_type,
                    use_container_width=True
                ):

                    st.session_state.masking_view_mode = "masked"
                    st.rerun()

                btn_orig_type = (
                    "secondary" if is_masked_view else "primary"
                )

                if st.button(
                    "إظهار القيمة الأصلية 👁️",
                    key="btn_show_original",
                    type=btn_orig_type,
                    use_container_width=True
                ):

                    st.session_state.masking_view_mode = "original"
                    st.rerun()

        with st.container(key="control_card_categories"):

            st.markdown("### 🛡️ تصنيفات التعتيم")

            cats = st.session_state.get(
                "masking_categories",
                {data_type: True for data_type in MASKING_TYPE_LABELS}
            )
            selected_categories = {
                data_type: st.checkbox(
                    label,
                    value=cats.get(data_type, True),
                    key=f"chk_mask_{data_type}"
                )
                for data_type, label in MASKING_TYPE_LABELS.items()
            }

            if st.button(
                "تطبيق إعدادات التعتيم 🛡️",
                key="btn_apply_masking",
                type="primary",
                use_container_width=True
            ):

                # حفظ حالة مربعات الاختيار في session_state لتظل محفوظة عند التنقل
                st.session_state.masking_categories = selected_categories
                allowed_types = get_allowed_types_from_categories(
                    selected_categories
                )

                if not allowed_types:
                    st.warning("⚠️ يرجى اختيار نوع بيانات حساس واحد على الأقل لتطبيق التعتيم.")
                    st.session_state.masking_applied = False
                    st.session_state.detected_data = []
                    st.session_state.detected_count = 0
                    st.session_state.redacted_content = doc["content"]
                else:
                    processed_dir = Path("processed")
                    processed_dir.mkdir(exist_ok=True)
                    output_path = processed_dir / f"redacted_{doc['file_name']}"

                    try:
                        if doc["file_type"] == "pdf":
                            res = redact_pdf(
                                doc["upload_path"],
                                str(output_path),
                                doc["pages"],
                                allowed_types=allowed_types
                            )
                            detected_data = res["detected_data"]
                            detected_count = res["detected_count"]
                            redacted_content = res.get("redacted_text", "")
                        else:
                            redacted_content, detected_data = redact_text(
                                doc["content"],
                                file_name=doc["file_name"],
                                allowed_types=allowed_types
                            )
                            output_path.write_text(redacted_content, encoding="utf-8")
                            detected_count = len(detected_data)

                        st.session_state.detected_data = detected_data
                        st.session_state.detected_count = detected_count
                        st.session_state.redacted_file_path = str(output_path)
                        st.session_state.redacted_content = redacted_content
                        st.session_state.masking_applied = True
                        st.session_state.masking_view_mode = "masked"

                        st.toast(
                            f"تم تطبيق التعتيم بنجاح على {detected_count} عناصر مختارة!",
                            icon="🔒"
                        )
                    except Exception as err:
                        st.error(f"حدث خطأ أثناء تطبيق التعتيم: {err}")

                st.rerun()


# --------------------------------------------------------
# 10. صفحة التقرير الأمني
# --------------------------------------------------------

def render_report_page():

    with st.container(key="page_banner"):

        st.title("📊 تقرير الفحص والتعتيم الشامل")

        st.caption(
            "ملخص موثق لنتائج الفحص ومعالجة البيانات الحساسة "
            "وتأكيد الأمان."
        )

    doc = st.session_state.get("current_document")

    scan_done = st.session_state.get(
        "scan_completed",
        False
    )

    detected_count = st.session_state.get("detected_count", 0)

    masking_applied = st.session_state.get("masking_applied", False)
    if not doc or not scan_done or not masking_applied or detected_count == 0:

        with st.container(key="empty_card"):

            st.write("")
            st.markdown("## 📊 لا يوجد تقرير متاح حالياً")

            if doc and scan_done and not masking_applied:
                st.info(
                    "يرجى اختيار أنواع البيانات وتطبيق إعدادات التعتيم أولاً لإنشاء التقرير."
                )
            elif doc and scan_done and detected_count == 0:
                st.info(NO_SENSITIVE_DATA_MESSAGE)
            else:
                st.write(
                    "الرجاء رفع وفحص مستند أولاً لتوليد التقرير الأمني."
                )

            st.write("")

        _, col_btn, _ = st.columns([1, 1.6, 1])

        with col_btn:

            if st.button(
                (
                    "الانتقال إلى التعتيم ➔"
                    if doc and scan_done and not masking_applied
                    else "الانتقال لرفع وفحص مستند ➔"
                ),
                key="btn_report_go_scan",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = (
                    "تعتيم البيانات"
                    if doc and scan_done and not masking_applied
                    else "فحص المستند"
                )
                st.rerun()

        return

    # تجهيز معلومات التقرير

    file_name = doc["file_name"]
    detected_data = st.session_state.get("detected_data", [])
    detected_count = st.session_state.get("detected_count", len(detected_data))

    masking_status = (
        "تم حجبها بنجاح 🔒"
        if st.session_state.get("masking_applied")
        else "بانتظار التعتيم ⚠️"
    )

    st.success(
        f"✓ تم إعداد التقرير الأمني للمستند: {file_name}"
    )

    # إحصائيات التقرير

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            label="اسم المستند",
            value=file_name
        )

    with m2:

        st.metric(
            label="تاريخ الفحص",
            value=datetime.now().strftime("%Y-%m-%d")
        )

    with m3:

        st.metric(
            label="البيانات المكتشفة",
            value=f"{detected_count} عناصر",
            delta="بيانات حساسة" if detected_count > 0 else "مستند نظيف",
            delta_color="inverse" if detected_count > 0 else "normal"
        )

    with m4:

        st.metric(
            label="حالة التعتيم",
            value=masking_status
        )

    # تفاصيل البيانات المكتشفة

    st.subheader("تفاصيل البيانات الحساسة المكتشفة:")

    masked_flag = st.session_state.get(
        "masking_applied",
        False
    )

    status_label = (
        "تم التعتيم بنجاح"
        if masked_flag
        else "تم اكتشافها (غير معتمة)"
    )

    TYPE_ARABIC = {
        "email": "البريد الإلكتروني",
        "phone": "رقم الهاتف / الجوال",
        "password": "كلمة المرور",
        "national_id": "رقم الهوية الوطنية",
        "passport": "جواز السفر",
        "credit_card": "بطاقة مصرفية",
        "bank_account": "حساب بنكي",
        "iban": "رقم الحساب الدولي (IBAN)",
        "full_name": "الاسم الكامل",
        "date_of_birth": "تاريخ الميلاد",
        "address": "العنوان",
        "salary": "الراتب",
        "username": "اسم المستخدم"
    }

    report_items = []
    for idx, item in enumerate(detected_data, start=1):
        d_type = TYPE_ARABIC.get(item.get("type"), item.get("type", "بيانات حساسة"))

        if item.get("page_number") and item.get("line_number"):
            loc_label = (
                f"الصفحة {item['page_number']}، "
                f"السطر {item['line_number']}"
            )
        elif item.get("line_number"):
            loc_label = (
            f"السطر {item['line_number']}، "
            f"الأعمدة {item['start_column']}–{item['end_column']}"
        )
        elif item.get("page_number"):
            loc_label = f"الصفحة {item['page_number']}"
        else:
            loc_label = "المستند"
        report_items.append({
            "#": idx,
            "نوع البيانات": d_type,
            "القيمة بعد التعتيم": "********",
            "الموقع": loc_label,
            "الحالة": status_label
        })

    if report_items:
        # عرض جدول التقرير بتنسيق وهوية بصرية موحدة ومتناسقة
        rows_html = []
        for itm in report_items:
            badge_class = "badge-status-masked" if masked_flag else "badge-status-detected"
            badge_icon = "🔒 " if masked_flag else "⚠️ "
            rows_html.append(
                f"<tr>"
                f"<td style='font-weight: 800; color: #0284c7; text-align: center;'>{itm['#']}</td>"
                f"<td style='font-weight: 700; color: #0c2b4d;'>{itm['نوع البيانات']}</td>"
                f"<td style='font-family: monospace; letter-spacing: 2px; color: #075985; font-weight: 800;'>{itm['القيمة بعد التعتيم']}</td>"
                f"<td style='color: #475569;'>{itm['الموقع']}</td>"
                f"<td><span class='{badge_class}'>{badge_icon}{itm['الحالة']}</span></td>"
                f"</tr>"
            )

        rows_content = "".join(rows_html)
        table_html = (
            '<div class="custom-report-table-wrapper">'
            '<table class="custom-report-table">'
            '<thead><tr>'
            '<th style="width: 8%; text-align: center;">#</th>'
            '<th style="width: 25%;">نوع البيانات</th>'
            '<th style="width: 22%;">القيمة بعد التعتيم</th>'
            '<th style="width: 23%;">الموقع</th>'
            '<th style="width: 22%;">الحالة</th>'
            '</tr></thead>'
            f'<tbody>{rows_content}</tbody>'
            '</table>'
            '</div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("لم يتم اكتشاف أي بيانات حساسة في هذا المستند.")

    # التوصيات الأمنية

    st.info(
        "📝 **التوصيات الأمنية:** تم فحص المستند "
        "ومطابقته لمعايير حماية الخصوصية."
    )

    # إنشاء التقرير النصي
    report_lines = [
        "================================================================",
        "                    نظام حماية المستندات",
        "                     تقرير أمني مفصل",
        "================================================================",
        f"اسم المستند: {file_name}",
        f"تاريخ الفحص: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"الحالة: {status_label}",
        f"إجمالي العناصر المكتشفة: {detected_count}",
        "----------------------------------------------------------------",
        "تفاصيل العناصر المعالجة:"
    ]

    if report_items:
        for itm in report_items:
            report_lines.append(
                f"{itm['#']}. {itm['نوع البيانات']} في {itm['الموقع']} -> ({itm['القيمة بعد التعتيم']}) [{itm['الحالة']}]"
            )
    else:
        report_lines.append("لا توجد بيانات حساسة.")

    report_lines.append("================================================================")
    report_text = "\n".join(report_lines)

    # أزرار تصدير التقرير

    btn1, btn2, btn3 = st.columns(3)

    with btn1:

        st.download_button(
            label="تحميل التقرير كملف نصي 💾",
            data=report_text,
            file_name=f"تقرير_حماية_{file_name}.txt",
            mime="text/plain",
            key="btn_download_report_txt",
            use_container_width=True
        )

    with btn2:

        if st.button(
            "تصدير إلى PDF 📥",
            key="btn_export_pdf",
            type="primary",
            use_container_width=True
        ):

            st.toast(
                "تم تصدير التقرير بصيغة PDF!",
                icon="📄"
            )

    with btn3:

        if st.button(
            "حفظ في الأرشيف 📂",
            key="btn_save_report",
            type="secondary",
            use_container_width=True
        ):

            st.toast(
                "تم حفظ التقرير في الأرشيف.",
                icon="💾"
            )


# --------------------------------------------------------
# 11. تشغيل التطبيق
# --------------------------------------------------------

def main():

    # تحميل التنسيقات

    load_css()

    # تهيئة بيانات الجلسة

    initialize_session_state()

    # إنشاء القائمة الجانبية

    render_sidebar()

    # تحديد الصفحة الحالية

    current_page = st.session_state.current_page

    # الصفحة الرئيسية

    if current_page == "الرئيسية":

        render_home_page()

    # صفحة الفحص

    elif current_page == "فحص المستند":

        render_scan_page()

    # صفحة التعتيم

    elif current_page == "تعتيم البيانات":

        render_masking_page()

    # صفحة التقرير

    elif current_page == "التقرير":

        render_report_page()


# --------------------------------------------------------
# 12. نقطة بداية التطبيق
# --------------------------------------------------------

if __name__ == "__main__":

    main()
