from pathlib import Path

def read_txt(file_path):
   """
   قراءة محتوى ملف TXT وإرجاع النص المستخرج.
   """


   path = Path(file_path)

   if not path.exists():
       raise FileNotFoundError("الملف غير موجود.")

   if path.suffix.lower() != ".txt":
       raise ValueError("نوع الملف غير مدعوم. يرجى اختيار ملف TXT.")

   text = path.read_text(encoding="utf-8-sig")

   if not text.strip():
       raise ValueError("الملف فارغ ولا يحتوي على نص.")

   return text


