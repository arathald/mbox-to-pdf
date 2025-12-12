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

#### `sample_data/simple.mbox`
- 2 plain-text emails (no attachments)
- Dates spanning Jan 4-5, 2008
- Purpose: Basic parsing, grouping, HTML rendering tests

#### `sample_data/complex.mbox` (NEW)
- Multi-part emails with various attachment types
- HTML emails with inline images
- Mixed encodings and charsets
- Malformed headers and edge cases
- Contains:
  - Email with `.txt` attachment (plain text file)
  - Email with `.csv` attachment (spreadsheet data)
  - Email with `.xlsx` attachment (Excel workbook)
  - Email with `.docx` attachment (Word document)
  - Email with `.pdf` attachment (PDF document)
  - Email with image attachments (`.png`, `.jpg`)
  - Email with `.html` attachment (standalone HTML)
  - Email with `multipart/mixed` and `multipart/related` structures
  - Email with inline base64-encoded content

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
    """Corrupted attachment skipped with warning in logs."""
    
def test_unrecognized_attachment_type_handled(complex_fixture):
    """Unknown MIME types handled gracefully."""
    
def test_large_mbox_performance(complex_fixture):
    """1000+ emails convert in < 30 seconds."""
```

### Fixtures

#### Pytest Fixtures
```python
@pytest.fixture
def simple_fixture(tmp_path):
    """Path to sample_data/simple.mbox for basic tests."""
    return Path(__file__).parent.parent / "sample_data" / "simple.mbox"

@pytest.fixture
def complex_fixture(tmp_path):
    """Path to sample_data/complex.mbox for comprehensive tests."""
    return Path(__file__).parent.parent / "sample_data" / "complex.mbox"

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for PDF output."""
    return tmp_path / "output"
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
