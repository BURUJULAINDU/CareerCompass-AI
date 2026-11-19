"""Tests: PDF/DOCX upload, text extraction, invalid files, privacy masking."""
import unittest
import conftest_path as cp
from resume_parser import ResumeError, extract_text, mask_pii, parse_resume, validate_upload


def sample(ext: str) -> bytes:
    return (cp.SAMPLES / f"sample_resume.{ext}").read_bytes()


class TestResumeExtraction(unittest.TestCase):
    def test_pdf_upload_extracts_text(self):
        text = extract_text("resume.pdf", sample("pdf"))
        self.assertIn("Python", text)

    def test_docx_upload_extracts_text(self):
        text = extract_text("resume.docx", sample("docx"))
        self.assertIn("SQL", text)

    def test_txt_upload_extracts_text(self):
        self.assertIn("Pandas", extract_text("resume.txt", sample("txt")))

    def test_invalid_extension_rejected(self):
        with self.assertRaises(ResumeError):
            validate_upload("resume.exe", b"abc")

    def test_empty_file_rejected(self):
        with self.assertRaises(ResumeError):
            extract_text("resume.pdf", b"")

    def test_oversized_file_rejected(self):
        with self.assertRaises(ResumeError):
            validate_upload("resume.pdf", b"x" * (6 * 1024 * 1024))

    def test_corrupted_pdf_rejected(self):
        with self.assertRaises(ResumeError):
            extract_text("resume.pdf", b"this is not a real pdf file at all" * 5)

    def test_corrupted_docx_rejected(self):
        with self.assertRaises(ResumeError):
            extract_text("resume.docx", b"not a zip archive" * 5)

    def test_image_only_or_blank_text_rejected(self):
        with self.assertRaises(ResumeError):
            extract_text("resume.txt", b"   \n  ")


class TestResumeParsing(unittest.TestCase):
    def setUp(self):
        self.parsed = parse_resume(extract_text("r.txt", sample("txt")))

    def test_sections_detected(self):
        for sec in ("education", "experience", "projects", "certifications", "skills"):
            self.assertIn(sec, self.parsed["sections_found"])

    def test_education_extracted(self):
        self.assertTrue(any("Data Science" in line for line in self.parsed["education"]))

    def test_certifications_extracted(self):
        self.assertEqual(len(self.parsed["certifications"]), 2)

    def test_contact_details_masked(self):
        masked = mask_pii("Email: a.b@example.com Phone: +91 98765 43210")
        self.assertNotIn("example.com", masked)
        self.assertNotIn("98765", masked)


if __name__ == "__main__":
    unittest.main()
