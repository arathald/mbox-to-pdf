"""
Error handling for mbox-to-pdf conversion.

This module provides structured error handling for attachment processing failures.
All error classification and user-friendly message generation is centralized here.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.mbox_converter import Email


@dataclass
class AttachmentErrorInfo:
    """Structured info for displaying attachment error dialog.

    This dataclass contains all information needed to display a user-friendly
    error dialog when an attachment cannot be processed.

    Attributes:
        email_subject: Subject line of the email containing the attachment
        email_date: Formatted date string (e.g., "Mon, January 13, 2008 at 2:30 PM")
        email_from: Sender address
        attachment_filename: Name of the attachment file
        mime_type: MIME type of the attachment
        file_size: Human-readable size (e.g., "256 KB")
        error_type: Category of error (corrupted, unsupported, etc.)
        error_message: User-friendly explanation of the error
    """
    email_subject: str
    email_date: str
    email_from: str
    attachment_filename: str
    mime_type: str
    file_size: str
    error_type: str
    error_message: str


class AttachmentError(Exception):
    """Raised when an attachment cannot be processed.

    Carries structured email/attachment context for error dialog display.
    This exception is caught during conversion and converted to AttachmentErrorInfo
    for display in the GUI.

    Attributes:
        email: The Email object containing the attachment
        attachment_filename: Name of the attachment file
        mime_type: MIME type of the attachment
        file_size: Size in bytes
        error_type: Category of error
        original_exception: The underlying exception that caused the error
    """

    # User-friendly error messages for each error type
    ERROR_MESSAGES = {
        'corrupted': 'The file could not be read. It may be corrupted or incomplete.',
        'unsupported': 'This file type is not supported for rendering.',
        'too_large': 'The file exceeds the maximum size limit (100MB).',
        'encoding_error': 'The file encoding could not be determined.',
        'missing_library': 'A required library for processing this file type is not installed.',
        'unsupported_variant': 'This variant of the file format is not supported.',
        'password_protected': 'This file is password-protected and cannot be opened.',
        'empty_file': 'The file is empty and contains no data.',
        'unknown': 'The file could not be processed due to an unexpected error.',
    }

    def __init__(
        self,
        email: "Email",
        attachment_filename: str,
        mime_type: str,
        file_size: int,
        error_type: str,
        original_exception: Optional[Exception] = None,
    ):
        self.email = email
        self.attachment_filename = attachment_filename
        self.mime_type = mime_type
        self.file_size = file_size
        self.error_type = error_type
        self.original_exception = original_exception

        # Set exception message
        message = f"Failed to process attachment '{attachment_filename}': {self.ERROR_MESSAGES.get(error_type, 'Unknown error')}"
        super().__init__(message)

    def to_error_info(self) -> AttachmentErrorInfo:
        """Convert to displayable error info for dialog."""
        return AttachmentErrorInfo(
            email_subject=self.email.subject,
            email_date=self.email.date.strftime('%a, %B %d, %Y at %I:%M %p'),
            email_from=self.email.from_addr,
            attachment_filename=self.attachment_filename,
            mime_type=self.mime_type,
            file_size=format_file_size(self.file_size),
            error_type=self.error_type,
            error_message=self.ERROR_MESSAGES.get(self.error_type, 'The file could not be processed.'),
        )


def format_file_size(size_bytes: int) -> str:
    """Format byte size as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    if size_bytes < 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024:
            if unit == 'B':
                return f"{int(size_bytes)} B"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} GB"


def classify_attachment_error(
    original_exception: Exception,
    attachment_filename: str,
    mime_type: str,
) -> str:
    """Classify exception type into user-friendly error category.

    Args:
        original_exception: The underlying exception
        attachment_filename: Name of the file that failed
        mime_type: MIME type of the attachment

    Returns:
        error_type: One of 'corrupted', 'unsupported', 'too_large', 'encoding_error',
                    'missing_library', 'unsupported_variant', 'password_protected',
                    'empty_file', 'unknown'
    """
    exception_type = type(original_exception).__name__
    exception_msg = str(original_exception).lower()

    # Check for encoding errors
    if isinstance(original_exception, UnicodeDecodeError):
        return 'encoding_error'

    # Check for missing libraries
    if isinstance(original_exception, ImportError):
        return 'missing_library'

    # Check for file not found / IO errors
    if isinstance(original_exception, (FileNotFoundError, IOError, OSError)):
        if 'permission' in exception_msg:
            return 'corrupted'
        return 'corrupted'

    # Check for value/type errors that often indicate corruption
    if isinstance(original_exception, (ValueError, TypeError)):
        if 'password' in exception_msg or 'encrypted' in exception_msg:
            return 'password_protected'
        if 'empty' in exception_msg or 'no data' in exception_msg:
            return 'empty_file'
        if 'not supported' in exception_msg or 'unsupported' in exception_msg:
            return 'unsupported_variant'
        return 'corrupted'

    # Check for memory errors (file too large)
    if isinstance(original_exception, MemoryError):
        return 'too_large'

    # Check exception message for common patterns
    if 'password' in exception_msg or 'encrypted' in exception_msg:
        return 'password_protected'
    if 'corrupt' in exception_msg or 'invalid' in exception_msg:
        return 'corrupted'
    if 'not supported' in exception_msg or 'unsupported' in exception_msg:
        return 'unsupported_variant'

    # Check if mime type is explicitly unsupported
    if is_unsupported_file_type(mime_type, attachment_filename):
        return 'unsupported'

    return 'unknown'


# File types that are explicitly not supported for rendering
UNSUPPORTED_MIME_PREFIXES = {
    'audio/',       # MP3, WAV, FLAC, etc.
    'video/',       # MP4, AVI, MOV, etc.
}

UNSUPPORTED_MIME_TYPES = {
    'application/x-zip-compressed',
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed',
    'application/x-tar',
    'application/gzip',
    'application/x-executable',
    'application/x-msdownload',  # .exe, .dll
    'application/x-shockwave-flash',
    'application/java-archive',
}

UNSUPPORTED_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib',  # Executables
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',  # Archives
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',  # Audio
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',  # Video
    '.swf', '.jar',  # Other binary
}


def is_unsupported_file_type(mime_type: str, filename: str) -> bool:
    """Check if file type is explicitly unsupported.

    Args:
        mime_type: MIME type of the attachment
        filename: Filename including extension

    Returns:
        True if the file type cannot be rendered in PDFs
    """
    mime_type = mime_type.lower()

    # Check MIME type prefixes (audio/*, video/*)
    for prefix in UNSUPPORTED_MIME_PREFIXES:
        if mime_type.startswith(prefix):
            return True

    # Check exact MIME types
    if mime_type in UNSUPPORTED_MIME_TYPES:
        return True

    # Check file extension
    filename_lower = filename.lower()
    for ext in UNSUPPORTED_EXTENSIONS:
        if filename_lower.endswith(ext):
            return True

    return False


# Maximum attachment size (100 MB)
MAX_ATTACHMENT_SIZE = 100 * 1024 * 1024


def check_attachment_size(size_bytes: int) -> bool:
    """Check if attachment size is within limits.

    Args:
        size_bytes: Size of attachment in bytes

    Returns:
        True if size is acceptable, False if too large
    """
    return size_bytes <= MAX_ATTACHMENT_SIZE
