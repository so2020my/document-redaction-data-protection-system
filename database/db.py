
import sqlite3
from pathlib import Path

# مسار قاعدة البيانات داخل مجلد database
DB_PATH = Path(__file__).parent / "redaction.db"


def get_connection():
    """إنشاء اتصال بقاعدة البيانات."""
    return sqlite3.connect(DB_PATH)


def create_tables():
    """إنشاء جدول البيانات الحساسة."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensitive_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            data_type TEXT NOT NULL,
            original_value TEXT NOT NULL,
            page_number INTEGER,
            start_position INTEGER,
            end_position INTEGER,
            x0 REAL,
            y0 REAL,
            x1 REAL,
            y1 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_sensitive_data(file_name, detected_data):
    """
    حفظ البيانات الحساسة الأصلية ومواضعها في SQLite.
    """

    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    for item in detected_data:

        rect = item.get("rect")

        # إحداثيات PDF، وتكون فارغة في TXT
        if rect:
            x0, y0, x1, y1 = rect
        else:
            x0 = y0 = x1 = y1 = None

        cursor.execute("""
            INSERT INTO sensitive_data (
                file_name,
                data_type,
                original_value,
                page_number,
                start_position,
                end_position,
                x0,
                y0,
                x1,
                y1
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_name,
            item["type"],
            item["value"],
            item.get("page_number"),
            item["start"],
            item["end"],
            x0,
            y0,
            x1,
            y1
        ))

    connection.commit()
    connection.close()

    return len(detected_data)


def get_sensitive_data(file_name):
    """
    استرجاع البيانات الحساسة الأصلية الخاصة بملف محدد.
    """

    create_tables()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            file_name,
            data_type,
            original_value,
            page_number,
            start_position,
            end_position,
            x0,
            y0,
            x1,
            y1,
            created_at
        FROM sensitive_data
        WHERE file_name = ?
        ORDER BY id
    """, (file_name,))

    rows = cursor.fetchall()
    connection.close()

    columns = [
        "id",
        "file_name",
        "type",
        "value",
        "page_number",
        "start",
        "end",
        "x0",
        "y0",
        "x1",
        "y1",
        "created_at"
    ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]
