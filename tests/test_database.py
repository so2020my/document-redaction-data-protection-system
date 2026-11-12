import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch

from database import db


class TestDatabase(unittest.TestCase):

    def test_save_sensitive_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            test_db = Path(temp_dir) / "test.db"

            with patch.object(db, "DB_PATH", test_db):

                data = [
                    {
                        "type": "email",
                        "value": "test@example.com",
                        "start": 7,
                        "end": 23
                    }
                ]

                count = db.save_sensitive_data(
                    "sample.txt",
                    data
                )

                connection = sqlite3.connect(test_db)
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT file_name, data_type, original_value,
                           start_position, end_position
                    FROM sensitive_data
                """)

                result = cursor.fetchone()
                connection.close()

                self.assertEqual(count, 1)
                self.assertEqual(result[0], "sample.txt")
                self.assertEqual(result[1], "email")
                self.assertEqual(result[2], "test@example.com")
                self.assertEqual(result[3], 7)
                self.assertEqual(result[4], 23)

    def test_get_sensitive_data(self):
            with tempfile.TemporaryDirectory() as temp_dir:
    
                test_db = Path(temp_dir) / "test.db"
    
                with patch.object(db, "DB_PATH", test_db):
    
                    data = [
                        {
                            "type": "email",
                            "value": "test@example.com",
                            "start": 7,
                            "end": 23
                        }
                    ]
    
                    db.save_sensitive_data("sample.txt", data)
    
                    result = db.get_sensitive_data("sample.txt")
    
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]["type"], "email")
                    self.assertEqual(result[0]["value"], "test@example.com")
                    self.assertEqual(result[0]["start"], 7)
                    self.assertEqual(result[0]["end"], 23)
                


if __name__ == "__main__":
    unittest.main()
