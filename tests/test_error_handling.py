"""
Tests for error handling module.
"""

from datetime import datetime, timezone

import pytest

from src.error_handling import (
    AttachmentError,
    AttachmentErrorInfo,
    classify_attachment_error,
    format_file_size,
    is_unsupported_file_type,
    check_attachment_size,
    MAX_ATTACHMENT_SIZE,
)
from src.mbox_converter import Email


@pytest.fixture
def sample_email():
    """Create a sample email for testing."""
    return Email(
        message_id="<test123@example.com>",
        from_addr="sender@example.com",
        to_addr="recipient@example.com",
        date=datetime(2008, 1, 15, 14, 30, tzinfo=timezone.utc),
        subject="Test Email Subject",
        body_text="Test body content",
    )


class TestFormatFileSize:
    """Tests for format_file_size function."""

    def test_bytes(self):
        assert format_file_size(500) == "500 B"

    def test_kilobytes(self):
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"

    def test_megabytes(self):
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"

    def test_gigabytes(self):
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_zero(self):
        assert format_file_size(0) == "0 B"

    def test_negative(self):
        assert format_file_size(-100) == "0 B"


class TestIsUnsupportedFileType:
    """Tests for is_unsupported_file_type function."""

    def test_audio_files_unsupported(self):
        assert is_unsupported_file_type("audio/mpeg", "song.mp3") is True
        assert is_unsupported_file_type("audio/wav", "sound.wav") is True

    def test_video_files_unsupported(self):
        assert is_unsupported_file_type("video/mp4", "video.mp4") is True
        assert is_unsupported_file_type("video/quicktime", "movie.mov") is True

    def test_archive_files_unsupported(self):
        assert is_unsupported_file_type("application/zip", "archive.zip") is True
        assert is_unsupported_file_type("application/x-rar-compressed", "archive.rar") is True

    def test_executable_files_unsupported(self):
        assert is_unsupported_file_type("application/x-msdownload", "program.exe") is True

    def test_text_files_supported(self):
        assert is_unsupported_file_type("text/plain", "notes.txt") is False

    def test_image_files_supported(self):
        assert is_unsupported_file_type("image/png", "photo.png") is False
        assert is_unsupported_file_type("image/jpeg", "photo.jpg") is False

    def test_pdf_files_supported(self):
        # PDF is "supported" in the sense we show a reference, not unsupported
        assert is_unsupported_file_type("application/pdf", "document.pdf") is False

    def test_extension_detection(self):
        # Even with generic mime type, extension should be detected
        assert is_unsupported_file_type("application/octet-stream", "video.mp4") is True
        assert is_unsupported_file_type("application/octet-stream", "archive.zip") is True


class TestClassifyAttachmentError:
    """Tests for classify_attachment_error function."""

    def test_unicode_decode_error(self):
        error = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
        result = classify_attachment_error(error, "file.txt", "text/plain")
        assert result == "encoding_error"

    def test_import_error(self):
        error = ImportError("No module named 'openpyxl'")
        result = classify_attachment_error(error, "data.xlsx", "application/vnd.openxmlformats")
        assert result == "missing_library"

    def test_file_not_found(self):
        error = FileNotFoundError("No such file")
        result = classify_attachment_error(error, "missing.txt", "text/plain")
        assert result == "corrupted"

    def test_memory_error(self):
        error = MemoryError("Out of memory")
        result = classify_attachment_error(error, "huge.bin", "application/octet-stream")
        assert result == "too_large"

    def test_password_protected_message(self):
        error = ValueError("File is password protected")
        result = classify_attachment_error(error, "secret.xlsx", "application/vnd.openxmlformats")
        assert result == "password_protected"

    def test_encrypted_message(self):
        error = ValueError("Encrypted content")
        result = classify_attachment_error(error, "secret.pdf", "application/pdf")
        assert result == "password_protected"

    def test_corrupt_message(self):
        error = ValueError("Corrupt file header")
        result = classify_attachment_error(error, "bad.xlsx", "application/vnd.openxmlformats")
        assert result == "corrupted"

    def test_unsupported_variant(self):
        error = ValueError("Format not supported")
        result = classify_attachment_error(error, "old.doc", "application/msword")
        assert result == "unsupported_variant"

    def test_empty_file(self):
        error = ValueError("Empty file - no data")
        result = classify_attachment_error(error, "empty.csv", "text/csv")
        assert result == "empty_file"

    def test_unsupported_mime_type(self):
        error = RuntimeError("Unknown error")
        result = classify_attachment_error(error, "song.mp3", "audio/mpeg")
        assert result == "unsupported"

    def test_unknown_error(self):
        error = RuntimeError("Something went wrong")
        result = classify_attachment_error(error, "file.txt", "text/plain")
        assert result == "unknown"


class TestAttachmentError:
    """Tests for AttachmentError exception class."""

    def test_error_creation(self, sample_email):
        error = AttachmentError(
            email=sample_email,
            attachment_filename="document.xlsx",
            mime_type="application/vnd.openxmlformats",
            file_size=1024,
            error_type="corrupted",
        )

        assert error.email == sample_email
        assert error.attachment_filename == "document.xlsx"
        assert error.error_type == "corrupted"
        assert "corrupted" in str(error).lower()

    def test_to_error_info(self, sample_email):
        error = AttachmentError(
            email=sample_email,
            attachment_filename="document.xlsx",
            mime_type="application/vnd.openxmlformats",
            file_size=2048,
            error_type="corrupted",
        )

        info = error.to_error_info()

        assert isinstance(info, AttachmentErrorInfo)
        assert info.email_subject == "Test Email Subject"
        assert info.email_from == "sender@example.com"
        assert info.attachment_filename == "document.xlsx"
        assert info.file_size == "2.0 KB"
        assert info.error_type == "corrupted"
        assert "corrupted" in info.error_message.lower()

    def test_error_messages(self, sample_email):
        error_types = [
            ("corrupted", "corrupted"),
            ("unsupported", "not supported"),
            ("too_large", "size limit"),
            ("encoding_error", "encoding"),
            ("missing_library", "library"),
            ("password_protected", "password"),
            ("empty_file", "empty"),
        ]

        for error_type, expected_in_message in error_types:
            error = AttachmentError(
                email=sample_email,
                attachment_filename="test.file",
                mime_type="application/octet-stream",
                file_size=1024,
                error_type=error_type,
            )
            info = error.to_error_info()
            assert expected_in_message in info.error_message.lower(), f"Expected '{expected_in_message}' in message for {error_type}"

    def test_with_original_exception(self, sample_email):
        original = ValueError("Original error")
        error = AttachmentError(
            email=sample_email,
            attachment_filename="test.file",
            mime_type="text/plain",
            file_size=100,
            error_type="corrupted",
            original_exception=original,
        )

        assert error.original_exception == original


class TestAttachmentErrorInfo:
    """Tests for AttachmentErrorInfo dataclass."""

    def test_dataclass_creation(self):
        info = AttachmentErrorInfo(
            email_subject="Test Subject",
            email_date="Tue, January 15, 2008 at 02:30 PM",
            email_from="sender@example.com",
            attachment_filename="document.pdf",
            mime_type="application/pdf",
            file_size="1.5 MB",
            error_type="unsupported",
            error_message="This file type is not supported.",
        )

        assert info.email_subject == "Test Subject"
        assert info.attachment_filename == "document.pdf"
        assert info.file_size == "1.5 MB"


class TestCheckAttachmentSize:
    """Tests for check_attachment_size function."""

    def test_small_file_ok(self):
        assert check_attachment_size(1024) is True

    def test_medium_file_ok(self):
        assert check_attachment_size(50 * 1024 * 1024) is True  # 50 MB

    def test_at_limit_ok(self):
        assert check_attachment_size(MAX_ATTACHMENT_SIZE) is True

    def test_over_limit_rejected(self):
        assert check_attachment_size(MAX_ATTACHMENT_SIZE + 1) is False

    def test_very_large_rejected(self):
        assert check_attachment_size(500 * 1024 * 1024) is False  # 500 MB
