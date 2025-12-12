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

## Implementation Plan

### Phase 1: Core Conversion Logic
- [ ] Implement `MboxConverter` class
- [ ] Implement email parsing from mbox files
- [ ] Implement date grouping logic (month/quarter/year)
- [ ] Implement HTML email rendering
- [ ] Implement PDF generation with weasyprint
- [ ] Write comprehensive unit tests

**Deliverable**: `src/mbox_converter.py` + `tests/test_mbox_converter.py`

### Phase 2: GUI Application
- [ ] Implement `MainWindow` with 5-step wizard
- [ ] Implement folder/file selection dialogs
- [ ] Implement progress tracking and display
- [ ] Implement error modal with copy/save functionality
- [ ] Integrate conversion logic with UI
- [ ] Test with sample.mbox file

**Deliverable**: `src/gui.py` + manual testing

### Phase 3: Error Handling & Logging
- [ ] Implement comprehensive error capture
- [ ] Implement log formatting for display/export
- [ ] Handle edge cases (bad encodings, corrupted mbox, etc.)
- [ ] Test error scenarios

**Deliverable**: `src/utils.py` + error integration

### Phase 4: Distribution & CI/CD
- [ ] Set up PyInstaller configuration
- [ ] Configure GitHub Actions workflow
- [ ] Build and test on all platforms
- [ ] Generate .exe, .dmg, AppImage artifacts

**Deliverable**: Standalone executables in CI/CD pipeline

### Phase 5: Documentation & Polish
- [ ] Write user guide
- [ ] Create example screenshots
- [ ] Security audit checklist
- [ ] Release notes

**Deliverable**: User-facing docs + v1.0 release

---

## Testing Strategy

### Unit Tests (`tests/test_mbox_converter.py`)

```python
def test_parse_simple_email():
    """Parse single email from sample.mbox."""
    
def test_parse_multiple_emails():
    """Parse all emails from sample.mbox."""
    
def test_group_by_month():
    """Emails grouped correctly by calendar month."""
    
def test_group_by_quarter():
    """Emails grouped correctly by quarter."""
    
def test_group_by_year():
    """Emails grouped correctly by year."""
    
def test_html_rendering():
    """Email converts to valid HTML."""
    
def test_pdf_generation():
    """HTML generates valid PDF file."""
    
def test_malformed_email():
    """Gracefully handle malformed headers."""
    
def test_unusual_encoding():
    """Handle UTF-8, Latin-1, mixed encodings."""
    
def test_large_mbox_file():
    """Performance with 1000+ emails."""
    
def test_empty_mbox_file():
    """Handle empty mbox gracefully."""
```

### Manual Testing

1. **Happy path**: Select Takeout folder → convert all files → check PDFs
2. **Partial selection**: Deselect some files → convert → verify only selected converted
3. **Different groupings**: Test month/quarter/year grouping outputs
4. **Error handling**: Try invalid folder, full disk, etc. → check error modal
5. **GUI flow**: Test back buttons, navigation between steps

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
