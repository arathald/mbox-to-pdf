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

### Architecture

```
┌─────────────────────────────────────────────────┐
│         GUI Layer (tkinter)                      │
│  - gui.py: MainWindow, wizard steps              │
│  - State management between steps                │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│      Conversion Layer (mbox_converter.py)        │
│  - MboxConverter class                           │
│  - Email parsing (stdlib mailbox module)         │
│  - HTML/PDF rendering (weasyprint)              │
│  - Grouping logic (month/quarter/year)          │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│      Utility Layer (utils.py)                    │
│  - Logging & error capture                       │
│  - Error modal display                           │
│  - File system operations                        │
└──────────────────────────────────────────────────┘
```

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
    errors: List[str]
    logs: str  # Full log text for display/export
    created_files: List[str]  # Paths to generated PDFs
```

**Class: `Email`**

```python
@dataclass
class Email:
    message_id: str
    from_addr: str
    to_addr: str
    date: datetime
    subject: str
    body_text: str
    body_html: Optional[str]
    headers: Dict[str, str]
```

#### `gui.py`

**Class: `MainWindow(tk.Tk)`**

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
- **Content**: 9 emails with various attachment types, encodings, and structures
- **Dates**: Jan 10-18, 2008
- **Purpose**: Comprehensive testing of parsing, attachment handling, rendering, error handling

**Emails in complex.mbox** (9 total):
1. **Text attachment** - `notes.txt` (project task list)
2. **CSV attachment** - `sales_q1.csv` (quarterly data, 3 months × 3 regions)
3. **Inline images** - Multipart/related with embedded PNG (base64)
4. **Mixed attachments** - `README.txt`, `data.csv`, `logo.png` (three files)
5. **Non-UTF8 encoding** - ISO-8859-1 charset with special characters (é, ñ, ü, ö)
6. **HTML attachment** - `report.html` (standalone HTML with table)
7. **Excel attachment** - `budget_2008.xlsx` (real XLSX workbook with formatted data)
8. **Word attachment** - `project_proposal.docx` (real DOCX with headings, lists, tables)
9. **PDF attachment** - `financial_report_q1.pdf` (real PDF document)

#### `sample_data/takeout_fixture/`
- **Location**: `sample_data/takeout_fixture/` (directory structure)
- **Fixture reference**: `takeout_fixture` (pytest fixture)
- **Purpose**: Realistic Gmail Takeout export structure for testing folder selection and multi-file conversion
- **Structure**: Mirrors actual Gmail Takeout directory layout

**Directory Structure**:
```
takeout_fixture/
├── Mail/
│   ├── All Mail.mbox         (9 emails - all messages)
│   ├── Drafts.mbox           (3 emails - user drafts)
│   ├── Sent Mail.mbox        (3 emails - sent messages)
│   └── Project Notes.mbox    (3 emails - custom label)
└── [Gmail]/
    ├── Important.mbox        (3 emails - Gmail system label)
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
