# REQUIREMENTS & DESIGN

## Overview

`mbox-to-pdf` is a privacy-first desktop application for converting Gmail Takeout MBOX email exports to PDF documents. The app is designed to be "luddite-proof"—requiring no technical knowledge to use, with clear error handling and helpful feedback.

## Requirements

### Functional Requirements

#### 1. Folder Selection (Step 1)
- User selects the root folder from their Gmail Takeout export
- Application scans folder for `.mbox` files
- Display list of all found mbox files with human-readable names
- Example:
  ```
  Takeout/
  └── Mail/
      ├── All Mail.mbox
      ├── Sent Mail.mbox
      ├── Drafts.mbox
      └── [Custom Label].mbox
  ```

#### 2. File Selection (Step 2)
- Display checkboxes for each discovered `.mbox` file
- All files checked by default
- Allow user to deselect any files they don't want converted
- Show total email count per file (if feasible)

#### 3. Grouping Selection (Step 3)
- Dropdown menu with three options:
  - **Calendar Month** (default): One PDF per month (e.g., `2008-01-January.pdf`)
  - **Quarter**: One PDF per quarter (e.g., `2008-Q1.pdf`)
  - **Calendar Year**: One PDF per year (e.g., `2008.pdf`)
- Apply grouping strategy to all selected mbox files

#### 4. Output Folder Selection (Step 4)
- File browser dialog
- User selects where to save output PDFs
- Default: same location as source Takeout folder (or Documents if unavailable)

#### 5. Conversion & Progress (Step 5)
- Show progress bar with current status
- Display estimated time remaining
- List of files being processed
- Cancel button (optional for v1)
- On success:
  - Confirmation message
  - "Open folder" button to show output directory
- On error:
  - Modal dialog with:
    - Human-readable error summary (top)
    - Full logs (scrollable area below)
    - **Copy to Clipboard** button
    - **Save as File** button (.txt, pre-formatted for email)

### Non-Functional Requirements

#### Security & Privacy
- ✅ 100% local processing—no network calls
- ✅ No external APIs or cloud services
- ✅ Standard, auditable Python libraries only
- ✅ Source code visible for auditing

#### Usability
- ✅ Zero command-line interaction
- ✅ Single executable file (Windows `.exe`, macOS `.dmg`, Linux AppImage)
- ✅ Wizard-style linear flow (no advanced options)
- ✅ Clear error messages with actionable guidance
- ✅ No configuration files required

#### Performance
- ✅ Handle mbox files up to 1GB+ efficiently
- ✅ PDF generation should not block UI (progress feedback)
- ✅ Reasonable time for 1000+ emails per file

#### Robustness
- ✅ Handle malformed mbox files gracefully
- ✅ Handle emails with unusual encodings (UTF-8, Latin-1, mixed)
- ✅ Skip unsupported content (attachments) without failing
- ✅ Validate output folder before starting conversion

---

## Design

### Architecture: API-First with Thin UI Layer

**Design Principle**: Business logic is testable independent of UI. The GUI is a thin presentation layer that calls the API and displays results.

```
┌────────────────────────────────────────────────────────┐
│  GUI Layer (tkinter) - Thin Presentation Layer         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ gui.py: MainWindow, wizard steps                 │  │
│  │ - Display folder/file selection dialogs          │  │
│  │ - Show progress bar during conversion            │  │
│  │ - Display error dialogs by calling error handler │  │
│  │ - NO business logic, NO error handling logic     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────┘
                 │ Calls API (no UI logic)
┌────────────────▼─────────────────────────────────────┐
│  Core API (Fully Testable)                            │
│                                                       │
│  mbox_converter.py:                                   │
│  ├─ MboxConverter class                              │
│  ├─ convert_mbox_files(paths, output_dir) → Result  │
│  ├─ discover_mbox_files(folder) → List[str]         │
│  └─ All parsing, rendering, grouping logic          │
│                                                       │
│  error_handling.py:                                   │
│  ├─ AttachmentError exception (with email context)  │
│  ├─ format_error_dialog(error) → UserFriendlyInfo   │
│  └─ All error classification & messages              │
│                                                       │
│  utils.py:                                            │
│  ├─ Logging, file operations, validation             │
│  └─ No UI-specific code                             │
│                                                       │
│  ConversionResult, AttachmentError, etc. (dataclasses)
└────────────────┬─────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │ Tests call API  │
        │ directly (no UI)│
        └─────────────────┘
```

**Functional Equivalence**: The API handles all errors/warnings identically whether called from UI or tests. Error messages, error dialogs, and retry logic are all in the API, not the UI.

### GUI Flow (5 Steps)

```
START
  ↓
Step 1: Folder Selection
  - File browser → Select Takeout root folder
  - Auto-scan for .mbox files
  - Display list
  - [Next] button
  ↓
Step 2: File Selection
  - Checkboxes for each .mbox file
  - [Uncheck] unwanted files
  - Show email count per file
  - [Back] [Next]
  ↓
Step 3: Grouping Strategy
  - Radio buttons: Month | Quarter | Year
  - Month selected by default
  - [Back] [Next]
  ↓
Step 4: Output Folder
  - File browser → Select output directory
  - [Back] [Next]
  ↓
Step 5: Convert & Progress
  - Progress bar (0-100%)
  - Current file being processed
  - Status text updates
  - On error: Error modal
    - [Copy Logs] [Save as File] [Close]
  - On success: Success screen
    - [Open Folder] [Close]
  ↓
END
```

---

## Email Document Specification

**Purpose**: Emails are rendered as formal documents suitable for legal, financial, and forensic use. All relevant information is preserved and clearly presented. Threads are properly attributed. Pages are clearly labeled.

### Email Header Rendering

Every email includes a **professional header section** with all relevant metadata:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         EMAIL DOCUMENT HEADER                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ Date: Monday, January 13, 2008 at 2:30 PM                                 │
│ From: alice@example.com                                                    │
│ To: bob@example.com                                                        │
│ Cc: charlie@example.com, diana@example.com                                 │
│ Subject: Q1 Budget Review Meeting                                          │
│ Message-ID: <budget-review-20080113@example.com>                           │
│ In-Reply-To: <previous-message-id@example.com> [if applicable]             │
│ References: [all related message IDs in thread]                            │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
```

**Header Fields** (in order):
1. **Date**: ISO 8601 format + human-readable (e.g., "Monday, January 13, 2008 at 2:30 PM")
2. **From**: Full email address (extract name if available, but preserve address)
3. **To**: All recipients (separated by commas and line breaks for readability)
4. **Cc**: Carbon copy recipients (if present)
5. **Bcc**: Blind copy recipients (if present and accessible)
6. **Subject**: Full subject line (preserve exactly as sent)
7. **Message-ID**: Unique identifier (for forensic/legal reference)
8. **In-Reply-To**: Reference to parent message (if this is a reply)
9. **References**: All message IDs in the conversation thread (comma-separated)
10. **X-Mailer**: Original email client (if present, for authenticity)

**HTML/CSS**:
```html
<div class="email-header">
  <div class="header-field">
    <span class="header-label">Date:</span>
    <span class="header-value">Monday, January 13, 2008 at 2:30 PM</span>
  </div>
  <div class="header-field">
    <span class="header-label">From:</span>
    <span class="header-value">alice@example.com</span>
  </div>
  <!-- ... more fields ... -->
</div>

<style>
.email-header {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 12px 15px;
  margin-bottom: 20px;
  font-family: monospace;
  font-size: 10pt;
  color: #333;
}

.header-field {
  display: flex;
  margin-bottom: 6px;
}

.header-label {
  font-weight: bold;
  min-width: 100px;
  color: #555;
}

.header-value {
  flex: 1;
  color: #222;
  word-break: break-word;
}
</style>
```

### Email Body Rendering

**Plain Text Emails**:
- Preserve line breaks exactly
- Preserve quoted text (lines starting with `>`)
- Use monospace font for legibility
- Wrap long lines gracefully

```html
<div class="email-body">
  <pre class="plaintext-body">Meeting is confirmed for Tuesday at 2pm.

Can you send the budget spreadsheet by Monday EOD?

Thanks,
Alice</pre>
</div>

<style>
.plaintext-body {
  font-family: "Courier New", monospace;
  font-size: 10pt;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #333;
  background-color: #fafafa;
  border: 1px solid #eee;
  padding: 12px;
  margin: 15px 0;
}
</style>
```

**HTML Emails**:
- Sanitize unsafe content (scripts, forms, links to external resources)
- Preserve semantic structure (headings, paragraphs, lists, tables)
- Preserve safe styling (colors, fonts, bold, italic)
- Preserve embedded images (base64-encoded)
- Mark external resources as references (don't embed)

```html
<div class="email-body">
  <div class="html-body">
    <!-- Original HTML rendered here (sanitized) -->
    <h2>Meeting Summary</h2>
    <p>Attendees:</p>
    <ul>
      <li>Alice</li>
      <li>Bob</li>
      <li>Charlie</li>
    </ul>
  </div>
</div>

<style>
.html-body {
  margin: 15px 0;
  line-height: 1.5;
  color: #333;
}
</style>
```

### Attachment Section

**Location**: Immediately after email body, before any forwarded content.

**Format**: Clear, labeled section with one line per attachment.

```html
<div class="attachments-section">
  <h3 class="attachments-header">Attachments (3 files)</h3>
  <ul class="attachments-list">
    <li class="attachment">
      <span class="attachment-icon">📎</span>
      <span class="attachment-name">budget_2008.xlsx</span>
      <span class="attachment-size">(1.2 MB)</span>
      <span class="attachment-type">[Embedded as table below]</span>
    </li>
    <li class="attachment">
      <span class="attachment-icon">📎</span>
      <span class="attachment-name">meeting-notes.docx</span>
      <span class="attachment-size">(45 KB)</span>
      <span class="attachment-type">[Embedded as text below]</span>
    </li>
    <li class="attachment">
      <span class="attachment-icon">📎</span>
      <span class="attachment-name">org-chart.png</span>
      <span class="attachment-size">(256 KB)</span>
      <span class="attachment-type">[Embedded as image below]</span>
    </li>
  </ul>
</div>
```

**CSS**:
```css
.attachments-section {
  background-color: #fff9e6;
  border-left: 4px solid #ffb84d;
  padding: 12px 15px;
  margin: 20px 0;
  page-break-inside: avoid;
}

.attachments-header {
  margin: 0 0 10px 0;
  font-size: 12pt;
  color: #333;
  font-weight: bold;
}

.attachments-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.attachment {
  display: flex;
  margin-bottom: 8px;
  font-size: 10pt;
  align-items: baseline;
  gap: 8px;
}

.attachment-icon {
  flex-shrink: 0;
  color: #666;
}

.attachment-name {
  font-family: monospace;
  color: #222;
  font-weight: 500;
}

.attachment-size {
  color: #888;
  font-size: 9pt;
}

.attachment-type {
  color: #666;
  font-size: 9pt;
  font-style: italic;
}
```

### Email Threading

**Scenario**: Email with `In-Reply-To` or `References` headers indicates it's part of a thread.

**Rendering**:
1. **Single email in thread**: Show header with In-Reply-To reference
2. **All thread emails in same PDF**: Show conversation chronologically
3. **Thread attribution**: Each message in thread clearly shows sender and date

**Example (Multiple emails in thread)**:

```html
<!-- Email 1 (oldest) -->
<div class="email-message">
  <div class="email-header">
    Date: January 10, 2008 at 9:00 AM
    From: alice@example.com
    To: bob@example.com
    Subject: Q1 Budget
  </div>
  <div class="email-body">
    We need to finalize the Q1 budget...
  </div>
</div>

<div class="thread-separator">
  ↓ Reply from Bob (January 10, 2008 at 10:30 AM)
</div>

<!-- Email 2 (reply) -->
<div class="email-message">
  <div class="email-header">
    Date: January 10, 2008 at 10:30 AM
    From: bob@example.com
    To: alice@example.com
    Subject: Re: Q1 Budget
  </div>
  <div class="email-body">
    I've reviewed the numbers. Some questions on Marketing...
  </div>
</div>

<div class="thread-separator">
  ↓ Reply from Alice (January 10, 2008 at 3:00 PM)
</div>

<!-- Email 3 (counter-reply) -->
<div class="email-message">
  ...
</div>
```

**CSS for Threading**:
```css
.email-message {
  margin: 0 0 30px 0;
  page-break-inside: avoid;
}

.thread-separator {
  text-align: center;
  margin: 25px 0;
  padding: 8px 0;
  border-top: 1px dashed #ccc;
  border-bottom: 1px dashed #ccc;
  font-size: 9pt;
  color: #999;
  font-style: italic;
}
```

### Page Layout & Breaks

**Page Formatting**:
- **Top margin**: 1 inch
- **Bottom margin**: 1 inch
- **Left margin**: 0.75 inches
- **Right margin**: 0.75 inches
- **Font**: 10pt serif (e.g., Times New Roman) for body, monospace for headers/code
- **Line spacing**: 1.5 (for readability and annotation space)

**Page Breaks**:
- Each **email** starts on a new page (clear separation for filing)
- Within long emails, natural breaks occur between email body and attachments
- Attachments stay with their email (don't orphan attachment from body)
- Thread continuations stay together if possible (multiple emails per page if they fit)

```html
<style>
@page {
  size: letter;
  margin: 1in 0.75in;
}

body {
  font-family: "Times New Roman", serif;
  font-size: 10pt;
  line-height: 1.5;
  color: #333;
}

.email-message {
  page-break-before: always;  /* Each email on new page */
  page-break-inside: avoid;   /* Don't break email content */
}

.email-header {
  page-break-inside: avoid;   /* Header stays with body */
}

.attachments-section {
  page-break-inside: avoid;   /* Attachments stay together */
}
</style>
```

### Long Email Handling

**Scenario**: Single email is multiple pages long (e.g., forwarded thread or long body).

**Rendering**:
- **Page 1**: Email header + start of body
- **Page 2+**: Continuation of email body
- **Header on continuation pages**: Repeat email subject at top of each page (optional, for legal documents)

```html
<!-- Page 1 -->
<div class="email-message">
  <div class="email-header">
    From: alice@example.com
    Subject: Project Proposal with History
  </div>
  <div class="email-body">
    Here is the full project proposal including all historical emails...
    [Page 1 content]
  </div>
</div>

<!-- Page 2 (automatic page break) -->
<div class="continuation-header">
  [Continued: Project Proposal with History - Page 2]
</div>
<div class="email-body-continuation">
  [Page 2 content - body continues]
</div>

<!-- Page 3 (attachments start) -->
<div class="continuation-header">
  [Continued: Project Proposal with History - Attachments]
</div>
<div class="attachments-section">
  <!-- Embedded attachments -->
</div>
```

**CSS for Continuation Pages**:
```css
.continuation-header {
  font-size: 9pt;
  color: #666;
  border-bottom: 1px solid #ddd;
  padding-bottom: 6px;
  margin-bottom: 12px;
  font-style: italic;
  page-break-after: avoid;
}

@media print {
  .continuation-header {
    display: block;  /* Show continuation markers in print */
  }
}
```

### Email as Forensic Document

**Completeness Requirements**:
- ✅ All headers preserved (Date, From, To, Cc, Bcc, Message-ID, etc.)
- ✅ Message-ID visible (unique identifier for reference)
- ✅ References/In-Reply-To visible (shows thread relationships)
- ✅ All attachments listed (even if not rendered)
- ✅ Attachment sizes visible (for completeness)
- ✅ Exact dates/times in standard format (no ambiguity)
- ✅ Clear threading attribution (who replied when)
- ✅ Page numbers (for large PDFs)
- ✅ Export date in footer (when document was created)

**Example PDF Footer** (optional, for large archives):
```html
<style>
@page {
  @bottom-center {
    content: "Page " counter(page) " of " counter(pages);
    font-size: 9pt;
    color: #999;
  }
  
  @bottom-left {
    content: "Generated: " string(export-date);
    font-size: 8pt;
    color: #ccc;
  }
}
</style>
```

### Core Modules


#### `mbox_converter.py`

**Class: `MboxConverter`**

```python
class MboxConverter:
    def __init__(self, grouping_strategy: str = "month"):
        """
        Args:
            grouping_strategy: "month", "quarter", or "year"
        """
        
    def convert_mbox_files(
        self,
        mbox_file_paths: List[str],
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> ConversionResult:
        """
        Convert multiple mbox files to PDFs.
        
        Args:
            mbox_file_paths: List of paths to .mbox files
            output_dir: Directory to save PDFs
            progress_callback: Function called with (current, total, filename)
        
        Returns:
            ConversionResult with success/failure status and logs
        """
        
    def _parse_mbox(self, mbox_path: str) -> List[Email]:
        """Parse single mbox file into Email objects."""
        
    def _group_emails_by_date(
        self,
        emails: List[Email]
    ) -> Dict[str, List[Email]]:
        """Group emails by strategy (month/quarter/year)."""
        
    def _render_email_to_html(self, email: Email) -> str:
        """Convert email message to HTML."""
        
    def _generate_pdf(
        self,
        html_content: str,
        output_path: str
    ) -> bool:
        """Render HTML to PDF using weasyprint."""
```

**Class: `ConversionResult`**

```python
@dataclass
class ConversionResult:
    success: bool
    pdfs_created: int
    errors: List[str]  # Human-readable error summaries for logs
    attachment_errors: List['AttachmentErrorInfo']  # For error dialogs
    logs: str  # Full log text for display/export
    created_files: List[str]  # Paths to generated PDFs
```

**Class: `AttachmentErrorInfo`** (for dialog display)

```python
@dataclass
class AttachmentErrorInfo:
    """Structured info for displaying attachment error dialog."""
    email_subject: str
    email_date: str  # Formatted date string
    email_from: str
    attachment_filename: str  # Including extension
    mime_type: str
    file_size: str  # Human-readable (e.g., "256 KB")
    error_type: str  # "corrupted", "unsupported", "too_large", etc.
    error_message: str  # User-friendly message (already localized)
```

**Class: `AttachmentError`** (exception, raised during conversion)

```python
class AttachmentError(Exception):
    """Raised when attachment cannot be processed.
    
    Carries structured email/attachment context for error dialog display.
    """
    def __init__(
        self,
        email: Email,
        attachment_filename: str,
        mime_type: str,
        file_size: int,
        error_type: str,  # "corrupted", "unsupported", "too_large", etc.
        original_exception: Exception = None
    ):
        self.email = email
        self.attachment_filename = attachment_filename
        self.mime_type = mime_type
        self.file_size = file_size
        self.error_type = error_type
        self.original_exception = original_exception
        
    def to_error_info(self) -> AttachmentErrorInfo:
        """Convert to displayable error info for dialog."""
        error_message = self._get_user_friendly_message()
        return AttachmentErrorInfo(
            email_subject=self.email.subject,
            email_date=self.email.date.strftime('%a, %B %d, %Y at %I:%M %p'),
            email_from=self.email.from_addr,
            attachment_filename=self.attachment_filename,
            mime_type=self.mime_type,
            file_size=self._format_size(self.file_size),
            error_type=self.error_type,
            error_message=error_message
        )
    
    def _get_user_friendly_message(self) -> str:
        """Return user-friendly error message (no technical details)."""
        messages = {
            'corrupted': 'The file could not be read. It may be corrupted or incomplete.',
            'unsupported': 'This file type is not supported for rendering.',
            'too_large': 'The file exceeds the maximum size limit (100MB).',
            'encoding_error': 'The file encoding could not be determined.',
            'missing_library': 'A required library for processing this file type is not installed.',
            'unsupported_variant': 'This variant of the file format is not supported.',
            'password_protected': 'This file is password-protected and cannot be opened.',
        }
        return messages.get(self.error_type, 'The file could not be processed.')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size as human-readable string."""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"
```

**Class: `Email`**

```python
@dataclass
class Email:
    """Email message with complete header information for forensic/legal documentation.
    
    All fields are preserved exactly as received (or empty if not present).
    This ensures the PDF archive is a complete and authentic record.
    """
    # Core identifiers
    message_id: str  # Unique message ID (e.g., '<abc123@example.com>')
    from_addr: str
    to_addr: str  # Comma-separated list of recipients
    
    # Thread information (for proper conversation rendering)
    cc_addr: Optional[str] = None  # Comma-separated CC recipients
    bcc_addr: Optional[str] = None  # Comma-separated BCC recipients
    in_reply_to: Optional[str] = None  # Message-ID of parent message
    references: Optional[List[str]] = None  # All message-IDs in thread
    
    # Content
    date: datetime
    subject: str
    body_text: str
    body_html: Optional[str]
    
    # Attachments (list of processed attachment objects)
    attachments: List['Attachment'] = None  # See Attachment dataclass
    
    # Complete header dict (for any missing fields)
    headers: Dict[str, str] = None
    
    # Additional forensic metadata
    x_mailer: Optional[str] = None  # Original email client (for authenticity)
    
    def render_header_html(self) -> str:
        """Render email header as professional HTML (for PDF).
        
        Returns formatted header section with all relevant fields.
        Suitable for legal/financial/forensic documentation.
        """
        
    def render_body_html(self) -> str:
        """Render email body as HTML (plain text or HTML email).
        
        - Plain text emails: wrapped in <pre> with preserved formatting
        - HTML emails: sanitized and rendered as-is
        """
        
    def format_date_for_display(self) -> str:
        """Return ISO 8601 + human-readable date (e.g., 'Monday, January 13, 2008 at 2:30 PM')."""

@dataclass
class Attachment:
    """Processed email attachment with size and rendering info."""
    filename: str
    mime_type: str
    size_bytes: int
    rendered_content: Optional[str] = None  # HTML content if successfully rendered
    content_type: str = None  # 'html', 'text', 'table', 'image', 'reference' (for PDF)
    error: Optional['AttachmentError'] = None  # If rendering failed
    
    def format_size_for_display(self) -> str:
        """Return human-readable size (e.g., '1.2 MB')."""
        
    def render_as_html(self) -> str:
        """Render attachment in HTML for PDF.
        
        Returns appropriate HTML based on type:
        - text → <pre class="code-block">
        - csv → <table>
        - xlsx → <table> (one per sheet)
        - docx → semantic HTML with headings/lists
        - html → sanitized <div>
        - image → <img src="data:...">
        - pdf → <p class="reference">
        - unsupported → <p class="attachment-error">
        """
```
```
```

#### `error_handling.py`

**Purpose**: Centralized error classification and user-friendly message generation. Ensures consistent error handling across API and UI.

**Functions**:

```python
def classify_attachment_error(
    original_exception: Exception,
    attachment_filename: str,
    mime_type: str
) -> str:
    """
    Classify exception type into user-friendly error category.
    
    Args:
        original_exception: The underlying exception
        attachment_filename: Name of the file that failed
        mime_type: MIME type of the attachment
        
    Returns:
        error_type: One of 'corrupted', 'unsupported', 'too_large', 'encoding_error',
                    'missing_library', 'unsupported_variant', 'password_protected'
    
    Examples:
        - UnicodeDecodeError → 'encoding_error'
        - ValueError (from openpyxl) → 'corrupted' or 'password_protected'
        - ImportError (missing library) → 'missing_library'
        - FileNotFoundError or OSError → 'corrupted'
        - Unknown MIME type → 'unsupported'
    """

def is_unsupported_file_type(mime_type: str, filename: str) -> bool:
    """Check if file type is explicitly unsupported."""
    unsupported_types = {
        'audio/*',  # MP3, WAV, etc.
        'video/*',  # MP4, AVI, etc.
        'application/x-zip-compressed',  # ZIP files
        'application/x-executable',  # EXE, DLL
        'application/octet-stream',  # Generic binary (usually unsupported)
    }
    # Check exact match and wildcard patterns
    ...
```

**UI Integration**:

```python
# In gui.py - display error dialog
from error_handling import AttachmentError, AttachmentErrorInfo

def show_attachment_error_dialog(error_info: AttachmentErrorInfo):
    """Display user-friendly attachment error dialog (non-blocking)."""
    dialog = ErrorModal(
        subject=error_info.email_subject,
        date=error_info.email_date,
        from_addr=error_info.email_from,
        filename=error_info.attachment_filename,
        mime_type=error_info.mime_type,
        error_message=error_info.error_message
    )
    # Non-blocking - returns immediately

def on_conversion_complete(result: ConversionResult):
    """Handle conversion completion - show error dialogs for each attachment error."""
    for error_info in result.attachment_errors:
        show_attachment_error_dialog(error_info)
    
    # Then show final success/failure modal
    show_conversion_summary(result)
```

#### `gui.py`

**Key Principle**: GUI is presentation-only. All business logic is in the API.

```python
class MainWindow(tk.Tk):
    def on_convert_clicked(self):
        """User clicked Convert button on Step 5."""
        # Call API directly (no conditional logic)
        result = self.converter.convert_mbox_files(
            mbox_file_paths=self.selected_files,
            output_dir=self.output_dir
        )
        
        # API returns structured result with errors
        # GUI just displays them
        if result.attachment_errors:
            for error_info in result.attachment_errors:
                self.show_attachment_error_dialog(error_info)
        
        if result.success:
            self.show_success_modal(result)
        else:
            self.show_error_modal(result)
```

**What GUI Does NOT Do**:
- ❌ Catch exceptions (API returns ConversionResult)
- ❌ Format error messages (API provides user-friendly text)
- ❌ Determine which attachments to skip (API decides and includes in result)
- ❌ Classify error types (error_handling.py handles this)

#### `mbox_converter.py`

```python
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mbox-to-pdf")
        self.geometry("600x400")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize GUI with Step 1 (folder selection)."""
        
    def show_step_1_folder_selection(self):
        """Display folder browser."""
        
    def show_step_2_file_selection(self, mbox_files: List[str]):
        """Display file checkboxes."""
        
    def show_step_3_grouping_selection(self):
        """Display grouping radio buttons."""
        
    def show_step_4_output_folder(self):
        """Display output folder browser."""
        
    def show_step_5_progress(self):
        """Display progress bar and status."""
        
    def show_error_modal(self, summary: str, logs: str):
        """Display error modal with copyable logs."""
        
    def show_success_modal(self, file_count: int, output_dir: str):
        """Display success modal with open folder button."""
```

#### `utils.py`

**Logging & Error Handling**

```python
class LogCapture:
    """Capture all logs and errors during conversion."""
    def get_logs() -> str:
        """Return formatted log text."""

class ErrorModal(tk.Toplevel):
    """Modal dialog for errors with copy/save buttons."""
    
def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard."""
    
def save_log_file(text: str, suggested_name: str) -> Optional[str]:
    """Open file dialog and save logs."""
    
def discover_mbox_files(root_dir: str) -> List[str]:
    """Recursively find all .mbox files in directory."""
    
def validate_output_directory(path: str) -> bool:
    """Check if path is writable directory."""
```

---

## Attachment Handling Specification

### Supported MIME Types

The application MUST handle the following attachment types by rendering them into the PDF output:

1. **Text Files** (`.txt`)
   - Plain rendering with line breaks preserved
   - Syntax highlighting optional
   - Display as pre-formatted code block

2. **Images** (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`)
   - Embed directly in PDF (base64 encoded)
   - Scale to fit page width (max 95% of page width)
   - Display filename and dimensions
   - Support both inline (multipart/related) and attachment

3. **Spreadsheets** (`.csv`, `.xlsx`)
   - **CSV**: Parse as tabular data, render as HTML table in PDF
     - Detect delimiter (comma, tab, semicolon)
     - Preserve cell formatting where possible
     - Handle quoted fields and escaped characters
   - **XLSX**: Extract all sheets, render as tables in PDF
     - Display sheet name as header
     - Convert cell values (formulas evaluated to their calculated values)
     - Style headers (bold, background color)
     - Preserve merged cells by spanning
     - Ignore VBA macros, pivot tables, charts

4. **Documents** (`.docx`)
   - Extract all text content preserving paragraphs
   - Preserve heading styles (H1, H2, etc.)
   - Preserve bold, italic, underline formatting
   - Skip complex elements: headers/footers, tables (extract as text), images
   - Display in readable, flowing format

5. **PDF Files** (`.pdf`)
   - Cannot embed PDF into PDF directly
   - Instead: Create reference section with filename, file size, and note "See attached PDF file"
   - Log warning that PDF attachment is available separately (not merged)

6. **HTML Files** (`.html`, `.htm`)
   - Parse and render HTML content directly into PDF
   - Sanitize unsafe HTML (scripts, style tags)
   - Preserve semantic markup (headings, lists, emphasis)
   - Handle embedded images (fetch from data URIs)

### Attachment Rendering Strategy

```
Email Body (always rendered)
├─ Email headers (From/To/Subject/Date)
├─ Body text (plain or HTML)
├─ Inline images (multipart/related)
└─ Attachments section (if any)
    ├─ .txt attachment
    │   └─ Rendered as code block
    ├─ .csv attachment
    │   └─ Rendered as table
    ├─ .xlsx attachment
    │   ├─ Sheet 1 (table)
    │   ├─ Sheet 2 (table)
    │   └─ ...
    ├─ .docx attachment
    │   └─ Text content extracted and formatted
    ├─ .png/.jpg attachment
    │   └─ Image embedded
    ├─ .html attachment
    │   └─ HTML rendered
    └─ .pdf attachment
        └─ Reference note (file not merged)
```

### Implementation Details

#### Attachment Extraction (`mbox_converter.py`)

```python
def extract_attachments(self, email_message: Message) -> List[Attachment]:
    """
    Extract all attachments from email.
    
    Returns:
        List of Attachment objects with:
        - filename: str
        - mime_type: str
        - content: bytes (raw content)
        - is_inline: bool (multipart/related vs multipart/mixed)
    """

def process_attachment(self, attachment: Attachment) -> str:
    """
    Convert attachment to HTML representation.
    
    Returns:
        HTML string to embed in PDF. If attachment cannot be processed,
        returns reference note instead.
    """
```

#### Attachment Converters (`src/attachment_handlers/`)

```python
# Optional: Separate module for each handler
handlers/
├── __init__.py
├── text_handler.py        # .txt
├── csv_handler.py         # .csv (→ HTML table)
├── xlsx_handler.py        # .xlsx (→ HTML tables)
├── docx_handler.py        # .docx (→ HTML text)
├── image_handler.py       # .png, .jpg, etc (→ base64 embed)
├── html_handler.py        # .html (→ sanitized HTML)
└── pdf_handler.py         # .pdf (→ reference note)
```

#### Handling Strategy for Complex Formats

**XLSX (Excel)**:
- Use `openpyxl` library to read workbook
- For each sheet:
  - Extract all used cells
  - Evaluate formulas to values (not the formula strings)
  - Convert to HTML `<table>`
  - Apply basic styling: header bold/background
- Skip: Charts, pivot tables, VBA, conditional formatting, data validation

**DOCX (Word)**:
- Use `python-docx` library to read document
- Extract paragraphs preserving:
  - Heading styles (convert to `<h1>`, `<h2>`, etc.)
  - Text styling (bold → `<strong>`, italic → `<em>`)
  - Lists (convert to `<ul>` or `<ol>`)
  - Line breaks
- Skip: Headers/footers, footnotes, tables (extract as text), images

**CSV**:
- Detect delimiter: Try comma, tab, semicolon (try each, pick best fit)
- Use Python's `csv` module for robust parsing
- Convert to HTML table with proper escaping
- No styling needed, just clean structure

### Error Handling for Attachments

```python
try:
    attachment_html = process_attachment(attachment)
except Exception as e:
    # Log error with attachment filename and MIME type
    logger.warning(f"Failed to process attachment {attachment.filename}: {e}")
    # Render fallback reference note instead
    attachment_html = render_attachment_reference(attachment)
```

**Fallback rendering** (if attachment cannot be processed):
```html
<div class="attachment-error">
  <strong>Attachment:</strong> {filename}
  <br/>
  <small>(Type: {mime_type}, Size: {file_size_kb}KB)</small>
  <br/>
  <em>This attachment could not be rendered into the PDF.</em>
</div>
```

### Attachment Error Dialog (User-Facing)

When an attachment cannot be processed, the application displays a **user-friendly warning dialog** to inform the user.

**Dialog Specification**:
```
┌─────────────────────────────────────────────────────────┐
│ ⚠️  Attachment Processing Error                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Could not process attachment in email                  │
│                                                         │
│ EMAIL DETAILS:                                          │
│   Subject: {email_subject}                              │
│   Date:    {email_date}                                 │
│   From:    {from_address}                               │
│                                                         │
│ ATTACHMENT:                                             │
│   Filename: {filename_with_extension}                   │
│   Type:     {mime_type}                                 │
│   Size:     {file_size}                                 │
│                                                         │
│ REASON:                                                 │
│   {error_message}                                       │
│                                                         │
│ ACTION:                                                 │
│   The attachment will be included as a reference note  │
│   in the PDF. The conversion will continue.             │
│                                                         │
│                                    [ OK ]              │
└─────────────────────────────────────────────────────────┘
```

**Error Messages (User-Friendly)**:
- **File appears to be corrupted**: "The file could not be read. It may be corrupted or incomplete."
- **File type not supported**: "This file type is not supported for rendering. (e.g., .exe, .zip)"
- **File is too large**: "The file exceeds the maximum size limit (100MB). Will be included as reference."
- **Cannot decode file**: "The file encoding could not be determined. Will be included as reference."
- **Missing required library**: "A required library for processing this file type is not installed."
- **Unsupported format variant**: "This variant of the file format is not supported. (e.g., password-protected Excel)"

**Implementation Details**:
- Dialog appears during conversion (Step 5)
- Non-blocking: User can click OK and conversion continues
- Does NOT include technical exception messages (user-friendly only)
- Full technical error logged to conversion logs for support/debugging
- Attachment still included in PDF as reference note (not skipped)
- Multiple attachment errors show one dialog per error (or batch summary option)

**Types of Attachments Requiring Error Dialogs**:
1. **Text files**: Encoding errors, binary file instead of text
2. **Images**: Corrupt image headers, unsupported formats (HEIF, WebP if not handled)
3. **Spreadsheets**: Password-protected, unsupported Excel versions, corrupted cells
4. **Documents**: Password-protected DOCX, corrupted structures
5. **PDF**: Encrypted PDFs, corrupted headers
6. **HTML**: Malformed HTML, circular references, excessively nested
7. **CSV**: Encoding issues, delimiter detection failed, huge line lengths

### File Type Coverage & Testing Requirements

The application MUST reliably handle the following attachment types. Each type has specific quality expectations:

#### 1. Text Files (`.txt`)
- **Must work**: Plain ASCII, UTF-8, common encodings (Latin-1, UTF-16)
- **Testing**: Simple task lists, code snippets, logs, notes
- **Complex.mbox**: `notes.txt` (project task list)
- **Error handling**: Graceful fallback if encoding unknown
- **Rendering**: Preserve line breaks, monospace font in PDF

#### 2. Spreadsheet Data (`.csv`)
- **Must work**: Standard comma/tab/semicolon delimiters, quoted fields, escape sequences
- **Testing**: Sales data, financial records, inventory lists
- **Complex.mbox**: `sales_q1.csv` (3-month data, 3 regions)
- **Error handling**: Automatic delimiter detection, graceful degradation
- **Rendering**: HTML table with proper column alignment

#### 3. Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`)
- **Must work**: Common formats, various dimensions, EXIF data
- **Testing**: Screenshots, photos, diagrams, logos, both inline and attached
- **Complex.mbox**: `logo.png` (3 total: inline + 2 attachments)
- **Error handling**: Corrupt header detection, unsupported variants
- **Rendering**: Base64 embedding, proper scaling, alt text with filename

#### 4. Spreadsheets (`.xlsx`)
- **Must work**: Modern Excel files, multiple sheets, basic formatting, formulas
- **Testing**: Budgets, financial reports, project schedules, sales data
- **Complex.mbox**: `budget_2008.xlsx` (real Excel, 1 sheet, numeric data, bold headers)
- **Quality requirements**:
  - Extract all sheets
  - Evaluate formulas to values (not formula strings)
  - Preserve bold/italic formatting
  - Preserve merged cells
  - Handle numeric formatting (currency, percentages)
- **Error handling**: Password-protected files, unsupported versions, corrupted sheets
- **Rendering**: Separate table per sheet, sheet name as header

#### 5. Documents (`.docx`)
- **Must work**: Modern Word documents, common formatting, tables, lists, images
- **Testing**: Proposals, reports, memos, structured documents
- **Complex.mbox**: `project_proposal.docx` (real DOCX, headings, lists, table)
- **Quality requirements**:
  - Extract all text preserving paragraph breaks
  - Preserve heading hierarchy (H1, H2, H3, etc.)
  - Preserve text styling (bold, italic, underline)
  - Preserve lists (bullets, numbered)
  - Handle tables (extract as formatted text or simple table)
- **Error handling**: Password-protected files, corrupted structures, unknown styles
- **Rendering**: Semantic HTML with proper heading tags

#### 6. HTML Files (`.html`, `.htm`)
- **Must work**: Valid HTML, CSS styling, embedded content
- **Testing**: Web pages, reports, documentation
- **Complex.mbox**: `report.html` (real HTML with table and styling)
- **Quality requirements**:
  - Preserve semantic structure (headings, paragraphs, lists)
  - Preserve safe styling (colors, fonts, sizing)
  - Handle embedded images (data URIs)
  - Sanitize unsafe content (scripts, forms)
- **Error handling**: Malformed HTML, circular includes, excessively nested
- **Rendering**: Direct HTML → PDF, styled appropriately

#### 7. PDF Files (`.pdf`)
- **Must work**: Standard PDFs, encrypted PDFs (warning), large PDFs
- **Testing**: Reports, certificates, archives, reference documents
- **Complex.mbox**: `financial_report_q1.pdf` (real PDF, formatted)
- **Quality requirements**:
  - Cannot embed PDF in PDF (technical limitation)
  - Must create reference note with filename, size, page count
  - Must warn if encrypted/password-protected
- **Error handling**: Encrypted PDFs (warn user), corrupted headers (reference only)
- **Rendering**: Reference block with metadata, note about availability separately

#### 8. Audio Files (`.mp3`, `.wav`, `.m4a`, etc.)
- **Support**: Not supported (explicitly unsupported file type)
- **Testing**: Meeting recordings, audio notes, podcasts
- **Complex.mbox**: `meeting-recording.mp3` (10th email)
- **Quality requirements**: None (intentionally unsupported)
- **Error handling**: Detect audio MIME types, trigger error dialog
- **Rendering**: Reference note with filename and size (cannot be embedded in PDF)

#### Coverage Matrix

| File Type | Complex.mbox | Tests | Error Dialog | Quality Level |
|-----------|------|-------|-------|---------------|
| .txt      | ✅ (notes.txt) | ✓ | ✓ | Must work perfectly |
| .csv      | ✅ (sales_q1.csv) | ✓ | ✓ | Must work perfectly |
| .png      | ✅ (logo.png ×3) | ✓ | ✓ | Must work perfectly |
| .jpg      | (future) | ✓ | ✓ | Should work |
| .xlsx     | ✅ (budget_2008.xlsx) | ✓ | ✓ | Must work perfectly |
| .docx     | ✅ (project_proposal.docx) | ✓ | ✓ | Must work perfectly |
| .html     | ✅ (report.html) | ✓ | ✓ | Must work perfectly |
| .pdf      | ✅ (financial_report_q1.pdf) | ✓ | ✓ | Reference only (OK) |
| .mp3      | ✅ (meeting-recording.mp3) | ✓ | ✓ | Unsupported (intentional) |

### Dependencies for Attachment Handling

Add to `requirements.txt`:
```
openpyxl>=3.10.0       # Excel (.xlsx)
python-docx>=0.8.11    # Word (.docx)
Pillow>=9.0.0          # Image processing
bleach>=5.0.0          # HTML sanitization
```

### PDF Styling for Attachments

```css
.attachment-section {
    margin-top: 20px;
    padding: 10px;
    border-top: 2px solid #333;
    page-break-inside: avoid;
}

.attachment-header {
    font-weight: bold;
    margin-bottom: 10px;
    background-color: #f0f0f0;
    padding: 5px;
}

.attachment-content {
    margin-left: 10px;
}

.csv-table, .xlsx-table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 10pt;
}

.csv-table th, .xlsx-table th {
    background-color: #e0e0e0;
    font-weight: bold;
    padding: 5px;
    border: 1px solid #ccc;
}

.csv-table td, .xlsx-table td {
    padding: 5px;
    border: 1px solid #ccc;
}

.attachment-reference {
    background-color: #fff3cd;
    padding: 10px;
    border-left: 4px solid #ffc107;
    margin: 10px 0;
}

.attachment-error {
    background-color: #f8d7da;
    padding: 10px;
    border-left: 4px solid #dc3545;
    margin: 10px 0;
    color: #721c24;
}
```

---

## Implementation Plan

### Phase 1: Core Conversion Logic
- [ ] Create comprehensive test fixtures (simple.mbox + complex.mbox with attachments)
- [ ] Implement `MboxConverter` class
- [ ] Implement email parsing from mbox files
- [ ] Implement date grouping logic (month/quarter/year)
- [ ] Implement basic HTML email rendering
- [ ] Write behavioral tests for all above (test-first)

**Deliverable**: `src/mbox_converter.py` + `tests/test_mbox_converter.py` with 40+ passing tests

### Phase 2: Attachment Handling
- [ ] Implement text file attachment rendering
- [ ] Implement image attachment embedding (PNG, JPG, GIF, WebP)
- [ ] Implement CSV attachment → HTML table conversion
- [ ] Implement XLSX attachment → HTML tables conversion (openpyxl)
- [ ] Implement DOCX attachment → HTML text extraction (python-docx)
- [ ] Implement HTML attachment rendering (bleach sanitization)
- [ ] Implement PDF attachment reference notes
- [ ] Write behavioral tests for each attachment type (test-first)
- [ ] Error handling and fallback rendering for unsupported formats

**Deliverable**: Attachment handlers + 30+ attachment-specific tests + updated complex.mbox fixture

### Phase 3: PDF Generation
- [ ] Implement HTML → PDF rendering with weasyprint
- [ ] Implement email header rendering (From/To/Subject/Date/CC)
- [ ] Implement page breaks and multi-page handling
- [ ] Implement CSS styling for clean PDF output
- [ ] Implement multiple emails concatenation in single PDF
- [ ] Write behavioral tests for PDF output
- [ ] Test with complex.mbox (emails with attachments)

**Deliverable**: PDF generation + 20+ PDF-specific tests

### Phase 4: GUI Application
- [ ] Implement `MainWindow` with 5-step wizard
- [ ] Implement folder/file selection dialogs
- [ ] Implement progress tracking and display
- [ ] Implement error modal with copy/save functionality
- [ ] Integrate conversion logic with UI
- [ ] Test with sample.mbox and complex.mbox files

**Deliverable**: `src/gui.py` + manual testing completed

### Phase 5: Error Handling & Logging
- [ ] Implement comprehensive error capture
- [ ] Implement log formatting for display/export
- [ ] Handle edge cases (bad encodings, corrupted mbox, malformed headers)
- [ ] Test error scenarios with complex fixture

**Deliverable**: `src/utils.py` + error handling integration

### Phase 6: Distribution & CI/CD
- [ ] Set up PyInstaller configuration
- [ ] Configure GitHub Actions workflow for multi-platform builds
- [ ] Build and test on Windows, macOS, Linux
- [ ] Generate .exe, .dmg, AppImage artifacts

**Deliverable**: Standalone executables in CI/CD pipeline

### Phase 7: Documentation & Polish
- [ ] Write user guide
- [ ] Create example screenshots
- [ ] Security audit checklist
- [ ] Release notes

**Deliverable**: User-facing docs + v1.0 release

---

## Testing Strategy

### Test-Driven Development Approach

**Core Principle**: For each feature, implement behavioral tests FIRST, then implementation code.

**Workflow**:
1. Write acceptance/behavioral test in `tests/test_mbox_converter.py`
2. Run test (should fail—no implementation yet)
3. Implement feature in `src/mbox_converter.py`
4. Run test until passing
5. Commit feature + test together

This ensures:
- Clear specification of expected behavior
- 100% test coverage
- Tests serve as executable documentation
- Regressions caught immediately

### Test Fixtures

Test fixtures are located in `sample_data/` directory and referenced via pytest fixtures in test code.

#### `sample_data/simple.mbox`
- **Location**: `sample_data/simple.mbox`
- **Fixture reference**: `simple_fixture` (pytest fixture)
- **Content**: 2 plain-text emails (no attachments)
- **Dates**: Jan 4-5, 2008
- **Purpose**: Basic parsing, grouping, HTML rendering tests
- **Use cases**: 
  - `test_parse_simple_email(simple_fixture)`
  - `test_parse_multiple_emails(simple_fixture)`
  - `test_plain_text_email_to_html(simple_fixture)`

#### `sample_data/complex.mbox`
- **Location**: `sample_data/complex.mbox`
- **Fixture reference**: `complex_fixture` (pytest fixture)
- **Content**: 10 emails with 8+ attachment types (8 supported, 1 unsupported), encodings, and structures
- **Dates**: Jan 10-19, 2008
- **Purpose**: Comprehensive testing of parsing, attachment handling, error dialogs, rendering, and unsupported file detection

**Emails in complex.mbox** (10 total):
1. **Text attachment** - `notes.txt` (project task list)
2. **CSV attachment** - `sales_q1.csv` (quarterly data, 3 months × 3 regions)
3. **Inline images** - Multipart/related with embedded PNG (base64)
4. **Mixed attachments** - `README.txt`, `data.csv`, `logo.png` (three files)
5. **Non-UTF8 encoding** - ISO-8859-1 charset with special characters (é, ñ, ü, ö)
6. **HTML attachment** - `report.html` (standalone HTML with table)
7. **Excel attachment** - `budget_2008.xlsx` (real XLSX workbook with formatted data)
8. **Word attachment** - `project_proposal.docx` (real DOCX with headings, lists, tables)
9. **PDF attachment** - `financial_report_q1.pdf` (real PDF document)
10. **Unsupported file type** - `meeting-recording.mp3` (audio file for error dialog testing)

#### `sample_data/takeout_fixture/`
- **Location**: `sample_data/takeout_fixture/` (directory structure)
- **Fixture reference**: `takeout_fixture` (pytest fixture)
- **Purpose**: Realistic Gmail Takeout export structure for testing folder selection and multi-file conversion
- **Structure**: Mirrors actual Gmail Takeout directory layout

**Directory Structure**:
```
takeout_fixture/
├── Mail/
│   ├── All Mail.mbox         (19 emails - all messages)
│   ├── Drafts.mbox           (6 emails - user drafts)
│   ├── Sent Mail.mbox        (6 emails - sent messages)
│   └── Project Notes.mbox    (6 emails - custom label)
└── [Gmail]/
    ├── Important.mbox        (4 emails - Gmail system label)
    └── Spam.mbox             (0 emails - empty folder test)
```

**Testing Coverage**:
- User selects `takeout_fixture` folder (Step 1)
- Application discovers 6 .mbox files (Step 2 shows all)
- User can select/deselect any files (partial conversion test)
- Tests multi-file handling with same emails grouped differently
- Tests both custom labels (`Project Notes`) and system labels (`[Gmail]/Important`)
- Tests empty mbox files (`Spam.mbox`)
- Tests directory traversal and recursive file discovery

**Supported attachment types tested**:
- ✅ Text files (`.txt`)
- ✅ Spreadsheet data (`.csv`)
- ✅ Images (`.png` inline and as attachment)
- ✅ Spreadsheets (`.xlsx` with multiple sheets)
- ✅ Documents (`.docx` with formatting)
- ✅ HTML (`.html` standalone)
- ✅ PDF (`.pdf` - reference handling)
- ✅ Multipart structures (`multipart/mixed`, `multipart/related`)
- ✅ Character encoding variations (UTF-8, ISO-8859-1)

### Unit Tests (`tests/test_mbox_converter.py`)

#### Parsing Tests
```python
def test_parse_simple_email(simple_fixture):
    """Parse single plain-text email from simple.mbox."""
    
def test_parse_multiple_emails(simple_fixture):
    """Parse all emails from simple.mbox."""
    
def test_parse_email_with_attachments(complex_fixture):
    """Parse email with multiple attachment types."""
    
def test_extract_all_attachment_types(complex_fixture):
    """Extract text, csv, xlsx, docx, pdf, images, html."""
    
def test_handle_missing_headers(complex_fixture):
    """Gracefully handle missing Date/From/Subject headers."""
    
def test_handle_unusual_encoding(complex_fixture):
    """Parse UTF-8, Latin-1, mixed and declared charsets."""
```

#### Grouping Tests
```python
def test_group_by_month(complex_fixture):
    """Emails grouped correctly by calendar month."""
    
def test_group_by_quarter(complex_fixture):
    """Emails grouped correctly by quarter."""
    
def test_group_by_year(complex_fixture):
    """Emails grouped correctly by year."""
    
def test_empty_groups_not_created(complex_fixture):
    """Months/quarters/years with no emails not created."""
```

#### Rendering Tests
```python
def test_plain_text_email_to_html(simple_fixture):
    """Plain text email converts to valid HTML."""
    
def test_html_email_preserved(complex_fixture):
    """HTML email body preserved in output."""
    
def test_inline_images_embedded(complex_fixture):
    """Inline images rendered in PDF (base64 embedded)."""
    
def test_text_attachment_rendered(complex_fixture):
    """Text attachment rendered as section in PDF."""
    
def test_csv_attachment_formatted_as_table(complex_fixture):
    """CSV rendered as formatted HTML table in PDF."""
    
def test_xlsx_attachment_rendered_as_sheet(complex_fixture):
    """Excel sheet rendered as table; formulas evaluated to values."""
    
def test_docx_attachment_converted_to_text(complex_fixture):
    """DOCX content extracted and formatted in PDF."""
    
def test_pdf_attachment_included_as_reference(complex_fixture):
    """PDF attachment noted with filename/size in PDF."""
    
def test_image_attachment_embedded(complex_fixture):
    """Image attachment (.png, .jpg) embedded in PDF."""
    
def test_html_attachment_rendered(complex_fixture):
    """HTML attachment content rendered in PDF."""

#### Email Document Rendering Tests (Forensic/Legal)
```python
def test_email_header_rendered_with_all_fields(complex_fixture):
    """Email header includes: Date, From, To, Cc, Subject, Message-ID."""
    
def test_email_header_preserves_exact_addresses(complex_fixture):
    """Email addresses are exact (not modified or obfuscated)."""
    
def test_email_header_uses_readable_date_format(complex_fixture):
    """Date formatted as 'Monday, January 13, 2008 at 2:30 PM' (human-readable + ISO)."""
    
def test_message_id_visible_in_pdf(complex_fixture):
    """Message-ID field is visible in rendered header (for forensic reference)."""
    
def test_attachments_clearly_labeled(complex_fixture):
    """Attachments section header shows count and lists each file with size."""
    
def test_attachment_section_before_body(complex_fixture):
    """Attachment list appears immediately after header, before body text."""
    
def test_unsupported_attachment_listed_with_size(complex_fixture):
    """Unsupported attachments (MP3) shown in list with size; error dialog triggered separately."""
    
def test_email_threading_renders_conversation(complex_fixture):
    """If In-Reply-To present, shows parent message context."""
    
def test_email_thread_shows_attribution(complex_fixture):
    """Each message in thread shows: [Date] From [address] Subject [subject]."""
    
def test_long_email_has_continuation_markers(complex_fixture):
    """Multi-page emails show '[Continued: Subject - Page N]' on continuation pages."""
    
def test_page_breaks_between_emails(complex_fixture):
    """Each email starts on new page (clear separation for filing/scanning)."""
    
def test_email_complete_for_legal_purposes(complex_fixture):
    """All headers present: Message-ID, In-Reply-To, References, X-Mailer."""
    
def test_thread_references_shown(complex_fixture):
    """References field lists all message-IDs in conversation thread."""
```

#### PDF Generation Tests
```python
def test_pdf_generation_creates_file(complex_fixture):
    """HTML → PDF conversion produces valid PDF file."""
    
def test_pdf_includes_headers(complex_fixture):
    """PDF includes From/To/Subject/Date in header."""
    
def test_pdf_page_breaks(complex_fixture):
    """Large emails break appropriately across pages."""
    
def test_multiple_emails_concatenated(complex_fixture):
    """Multiple grouped emails concatenated in single PDF."""
    
def test_pdf_is_readable(complex_fixture):
    """Generated PDF can be opened and displays correctly."""
```

#### Error Handling Tests
```python
def test_malformed_mbox_file(complex_fixture):
    """Gracefully handle malformed mbox structure."""
    
def test_missing_mbox_file():
    """Proper error when mbox file doesn't exist."""
    
def test_empty_mbox_file(complex_fixture):
    """Handle empty mbox without crashing."""
    
def test_corrupted_attachment_skipped(complex_fixture):
    """Corrupted attachment triggers user warning dialog with details."""
    
def test_unrecognized_attachment_type_handled(complex_fixture):
    """Unknown MIME types trigger warning, fallback reference rendered."""
    
def test_attachment_error_dialog_displays_email_info(complex_fixture):
    """Error dialog shows: email subject, date, filename, extension, error message."""
    
def test_large_mbox_performance(complex_fixture):
    """1000+ emails convert in < 30 seconds."""
```

### Fixtures

#### Pytest Fixtures

These fixtures are defined in `tests/conftest.py` and used throughout test suite:

```python
from pathlib import Path
import pytest

@pytest.fixture
def simple_fixture():
    """
    Path to sample_data/simple.mbox for basic parsing tests.
    
    Location: mbox-to-pdf/sample_data/simple.mbox
    Contains: 2 plain text emails (Jan 4-5, 2008)
    """
    return Path(__file__).parent.parent / "sample_data" / "simple.mbox"

@pytest.fixture
def complex_fixture():
    """
    Path to sample_data/complex.mbox for comprehensive tests.
    
    Location: mbox-to-pdf/sample_data/complex.mbox
    Contains: 9 emails with 8 attachment types (Jan 10-18, 2008)
             - Text, CSV, XLSX, DOCX, PDF, HTML, PNG, mixed
    """
    return Path(__file__).parent.parent / "sample_data" / "complex.mbox"

@pytest.fixture
def takeout_fixture():
    """
    Path to sample_data/takeout_fixture/ directory for multi-file tests.
    
    Location: mbox-to-pdf/sample_data/takeout_fixture/
    Structure: Realistic Gmail Takeout export layout
    Contains:
      - Mail/All Mail.mbox (9 emails)
      - Mail/Drafts.mbox (3 emails)
      - Mail/Sent Mail.mbox (3 emails)
      - Mail/Project Notes.mbox (3 emails - custom label)
      - [Gmail]/Important.mbox (3 emails - system label)
      - [Gmail]/Spam.mbox (empty)
    
    Emulates real Gmail Takeout folder structure for testing:
    - Folder selection (Step 1)
    - Multiple .mbox file discovery (Step 2)
    - Partial selection of files
    - Multi-file conversion
    """
    return Path(__file__).parent.parent / "sample_data" / "takeout_fixture"

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for PDF output during tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

**Usage Examples**:
```python
def test_parse_simple_email(simple_fixture):
    """Use simple_fixture to test basic email parsing."""
    mbox = mailbox.mbox(str(simple_fixture))
    emails = list(mbox)
    assert len(emails) == 2

def test_xlsx_attachment_rendering(complex_fixture, temp_output_dir):
    """Use complex_fixture + temp_output_dir for integration test."""
    converter = MboxConverter()
    result = converter.convert_mbox_files(
        [str(complex_fixture)],
        str(temp_output_dir)
    )
    assert result.success
    assert result.pdfs_created >= 1

def test_discover_mbox_files_in_takeout(takeout_fixture):
    """Test file discovery in realistic Takeout structure."""
    # Simulate Step 1: folder selection
    discovered = discover_mbox_files(str(takeout_fixture))
    assert len(discovered) == 6
    assert any("All Mail" in f for f in discovered)
    assert any("[Gmail]" in f for f in discovered)

def test_multi_file_conversion(takeout_fixture, temp_output_dir):
    """Test conversion of multiple files from Takeout structure."""
    converter = MboxConverter()
    mbox_files = discover_mbox_files(str(takeout_fixture))
    
    # Simulate Step 2: user selects subset of files
    selected_files = [f for f in mbox_files if "All Mail" in f or "Drafts" in f]
    
    result = converter.convert_mbox_files(selected_files, str(temp_output_dir))
    assert result.success
    # Should create multiple PDFs (one per month or user selection)
    assert result.pdfs_created >= 2
```

### Manual Testing

1. **Happy path**: Select Takeout folder → convert all files → check PDFs
2. **Partial selection**: Deselect some files → convert → verify only selected converted
3. **Different groupings**: Test month/quarter/year grouping outputs
4. **Attachment handling**: Convert email with mixed attachments → verify PDF includes all
5. **Error handling**: Try invalid folder, full disk, corrupted file → check error modal
6. **GUI flow**: Test back buttons, navigation between steps
7. **Large files**: Convert 1000+ email mbox → verify performance and output

---

## Technical Decisions

### Why Weasyprint over ReportLab?

- **Weasyprint**: Pure Python, renders HTML → PDF (good for email HTML content)
- **ReportLab**: Lower-level, more control but requires manual layout

**Choice**: Weasyprint. Cleaner for email-to-PDF use case.

### Why Tkinter for GUI?

- Built-in with Python (no external dependencies)
- Cross-platform (Windows/macOS/Linux)
- Simple for this linear wizard workflow
- No need for complex UI framework

### Why Stdlib `mailbox` Module?

- Standard library (no extra dependencies)
- Handles mbox format parsing
- Robust handling of edge cases

---

## Known Limitations & Future Work

### v1.0 Scope (MVP)
- Single PDF per month/quarter/year (no custom ranges)
- No attachment extraction
- No interactive features (just email → PDF)
- No search/indexing of converted PDFs

### Future Enhancements
- Batch convert multiple Takeout exports
- Custom date ranges (e.g., "Q3 2023")
- Extract attachments to separate folder
- Full-text search of converted PDFs
- Dark mode UI
- Remember last used folder

---

## Security Considerations

### Verified
- ✅ No network calls
- ✅ No data transmission
- ✅ Standard library + weasyprint only
- ✅ Source code auditable on GitHub
- ✅ No tracking/analytics
- ✅ No config files (no data at rest)

### Not Implemented
- ❌ Encrypted PDF output (can add if requested)
- ❌ Secure deletion of temp files (not needed—temp OS cleanup sufficient)
- ❌ Code signing for executable (can add for distribution)

---

## Deployment

### Local Development
```bash
git clone <repo>
cd mbox-to-pdf
pip install -r requirements.txt
python src/gui.py
```

### Building Executables
Push to GitHub → GitHub Actions automatically builds:
- `mbox-to-pdf.exe` (Windows)
- `mbox-to-pdf.dmg` (macOS)
- `mbox-to-pdf` (Linux AppImage)

### Distribution
Users download `.exe` / `.dmg` / AppImage from GitHub Releases.

---

## Success Criteria

- [ ] Application launches without Python installed
- [ ] User can convert Takeout export in < 5 clicks
- [ ] Error messages are clear and actionable
- [ ] Logs can be easily copied/saved for support
- [ ] Conversion of 1000+ emails completes in < 30 seconds
- [ ] Cross-platform builds (Windows/macOS/Linux) work
- [ ] No external dependencies or network access
