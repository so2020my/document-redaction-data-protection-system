import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

import pymupdf

import interface.pages as pages
import detection.detector as detector_module
from file_processing.pdf_reader import read_pdf
from file_processing.txt_reader import read_txt


class _RerunRequested(BaseException):
    pass


class _SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __setattr__(self, name, value):
        self[name] = value


class _WidgetStub:
    def __getattr__(self, _name):
        return lambda *args, **kwargs: None


class _StreamlitStub:
    def __init__(self, session_state, clicked_button):
        self.session_state = session_state
        self.clicked_button = clicked_button
        self.markdown_calls = []

    def container(self, **_kwargs):
        return nullcontext()

    def columns(self, spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [nullcontext() for _ in range(count)]

    def button(self, _label, **kwargs):
        return kwargs.get("key") == self.clicked_button

    def markdown(self, text, **_kwargs):
        self.markdown_calls.append(text)

    def checkbox(self, *_args, **_kwargs):
        return False

    def progress(self, *_args, **_kwargs):
        return _WidgetStub()

    def empty(self):
        return _WidgetStub()

    def rerun(self):
        raise _RerunRequested

    def __getattr__(self, _name):
        return lambda *args, **kwargs: None


class TestScanAndMaskingPhases(unittest.TestCase):

    def _run_scan(self, doc):
        session_state = _SessionState({
            "current_document": doc,
            "scan_completed": False,
            "masking_applied": False,
            "detected_data": [],
            "detected_count": 0,
            "uploader_id": 0,
            "upload_error": None,
        })
        streamlit_stub = _StreamlitStub(
            session_state,
            clicked_button="btn_start_scan"
        )

        with (
            patch.object(pages, "st", streamlit_stub),
            patch.object(pages, "read_pdf", wraps=read_pdf) as pdf_reader,
            patch.object(pages, "read_txt", wraps=read_txt) as txt_reader,
            patch.object(detector_module, "detect_sensitive_data") as detector,
            patch.object(pages, "redact_pdf") as pdf_redactor,
            patch.object(pages, "redact_text") as txt_redactor,
            patch.object(pages, "get_allowed_types_from_categories") as get_types,
            patch.object(pages.time, "sleep"),
        ):
            with self.assertRaises(_RerunRequested):
                pages.render_scan_page()

        detector.assert_not_called()
        pdf_redactor.assert_not_called()
        txt_redactor.assert_not_called()
        get_types.assert_not_called()
        self.assertTrue(session_state["scan_completed"])
        self.assertFalse(session_state["masking_applied"])
        self.assertEqual(session_state["detected_data"], [])
        self.assertEqual(session_state["detected_count"], 0)
        return session_state, pdf_reader, txt_reader

    def test_pdf_scan_only_reads_and_extracts_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.pdf"
            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((50, 80), "Email: alice@example.com")
            document.save(path)
            document.close()

            session, pdf_reader, txt_reader = self._run_scan({
                "file_name": path.name,
                "file_size": "1 KB",
                "file_type": "pdf",
                "upload_path": str(path),
                "content": "stale preview",
                "pages": [],
            })

        pdf_reader.assert_called_once_with(str(path))
        txt_reader.assert_not_called()
        self.assertIn("alice@example.com", session["current_document"]["content"])

    def test_txt_scan_only_reads_and_extracts_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_text("Email: alice@example.com", encoding="utf-8")

            session, pdf_reader, txt_reader = self._run_scan({
                "file_name": path.name,
                "file_size": "1 KB",
                "file_type": "txt",
                "upload_path": str(path),
                "content": "stale preview",
                "pages": None,
            })

        txt_reader.assert_called_once_with(str(path))
        pdf_reader.assert_not_called()
        self.assertEqual(
            session["current_document"]["content"],
            "Email: alice@example.com"
        )

    def test_unchecking_every_category_stops_before_redaction(self):
        session_state = _SessionState({
            "current_document": {
                "file_name": "sample.txt",
                "file_size": "1 KB",
                "file_type": "txt",
                "upload_path": "unused.txt",
                "content": "Email: alice@example.com",
                "pages": None,
            },
            "scan_completed": True,
            "masking_applied": False,
            "masking_view_mode": "masked",
            "detected_data": [],
            "detected_count": 0,
            "redacted_file_path": None,
            "redacted_content": "",
            "masking_categories": {},
        })
        streamlit_stub = _StreamlitStub(
            session_state,
            clicked_button="btn_apply_masking"
        )

        with (
            patch.object(pages, "st", streamlit_stub),
            patch.object(detector_module, "detect_sensitive_data") as detector,
            patch.object(pages, "redact_pdf") as pdf_redactor,
            patch.object(pages, "redact_text") as txt_redactor,
        ):
            with self.assertRaises(_RerunRequested):
                pages.render_masking_page()

        detector.assert_not_called()
        pdf_redactor.assert_not_called()
        txt_redactor.assert_not_called()
        self.assertFalse(session_state["masking_applied"])
        self.assertEqual(session_state["detected_count"], 0)
        self.assertEqual(
            session_state["redacted_content"],
            "Email: alice@example.com"
        )
        self.assertEqual(
            pages.get_allowed_types_from_categories(
                session_state["masking_categories"]
            ),
            []
        )

    def test_report_keeps_type_labels_and_source_locations(self):
        session_state = _SessionState({
            "current_document": {"file_name": "sample.pdf"},
            "scan_completed": True,
            "detected_count": 2,
            "masking_applied": True,
            "detected_data": [
                {
                    "type": "full_name",
                    "line_number": 3,
                    "start_column": 4,
                    "end_column": 11,
                },
                {
                    "type": "salary",
                    "page_number": 2,
                    "line_number": 4,
                    "rect": [10, 20, 30, 40],
                },
            ],
        })
        streamlit_stub = _StreamlitStub(session_state, clicked_button=None)

        with patch.object(pages, "st", streamlit_stub):
            pages.render_report_page()

        report_html = "\n".join(streamlit_stub.markdown_calls)
        self.assertIn("الاسم الكامل", report_html)
        self.assertIn("الراتب", report_html)
        self.assertIn("السطر 3، الأعمدة 4–11", report_html)
        self.assertIn("الصفحة 2، السطر 4", report_html)


if __name__ == "__main__":
    unittest.main()
