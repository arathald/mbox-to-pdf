# CLAUDE.md - Project Guide for mbox-to-pdf

## Project Overview

**mbox-to-pdf** is a privacy-first desktop application for converting Gmail Takeout MBOX email exports to professionally formatted PDF documents. Designed to be "luddite-proof" with a 5-step wizard GUI requiring zero technical knowledge.

**Primary use cases**: Legal document discovery, financial records retention, forensic analysis, email archival.

## Tech Stack

- **Language**: Python 3.12+
- **PDF Generation**: xhtml2pdf (pure Python HTML → PDF, no native deps)
- **GUI Framework**: Tkinter (stdlib, cross-platform)
- **Email Parsing**: Python stdlib `mailbox` module
- **Attachment Handling**:
  - `openpyxl` - Excel (.xlsx)
  - `python-docx` - Word (.docx)
  - `Pillow` - Images (PNG, JPG, GIF, WebP)
  - `bleach` - HTML sanitization
- **Testing**: pytest, pytest-cov
- **Distribution**: PyInstaller (cross-platform executables)

## Project Structure

```
mbox-to-pdf/
├── src/
│   ├── mbox_converter.py   # Core API: parsing, grouping, rendering
│   ├── gui.py              # Tkinter GUI (thin presentation layer)
│   └── utils.py            # Logging, file ops, validation
├── tests/
│   └── test_mbox_converter.py  # Behavioral tests
├── sample_data/
│   ├── simple.mbox         # 2 plain-text emails (basic parsing tests)
│   ├── complex.mbox        # 10 emails, 8+ attachment types
│   └── takeout_fixture/    # Realistic Gmail Takeout structure
├── DESIGN.md               # Comprehensive requirements & design spec
├── requirements.txt
└── .github/workflows/      # CI/CD for multi-platform builds
```

## Key Commands

```bash
# Create and activate virtual environment (first time)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
PYTHONPATH=. pytest tests/

# Run tests with coverage
PYTHONPATH=. pytest tests/ --cov=src --cov-report=html

# Run the GUI application
PYTHONPATH=. python src/gui.py

# Lint/format
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Architecture: API-First Design

**Core principle**: Business logic is testable independent of UI. The GUI is a thin presentation layer.

```
┌─────────────────────────────────┐
│  GUI (tkinter) - Display only   │
│  - No business logic            │
│  - No error handling logic      │
│  - Calls API, displays results  │
└────────────┬────────────────────┘
             │ Calls API
┌────────────▼────────────────────┐
│  Core API (Fully Testable)      │
│  - mbox_converter.py            │
│  - error_handling.py            │
│  - utils.py                     │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Tests call API directly        │
│  (no UI dependencies)           │
└─────────────────────────────────┘
```

## Test Fixtures

Tests use pytest fixtures defined in `tests/conftest.py`:

- **`simple_fixture`** → `sample_data/simple.mbox` (2 plain-text emails)
- **`complex_fixture`** → `sample_data/complex.mbox` (10 emails with attachments)
- **`takeout_fixture`** → `sample_data/takeout_fixture/` (realistic Gmail Takeout structure)
- **`temp_output_dir`** → Temporary directory for PDF output

## Supported Attachment Types

| Type | Extension | Rendering |
|------|-----------|-----------|
| Text | `.txt` | Monospace code block |
| CSV | `.csv` | HTML table |
| Excel | `.xlsx` | HTML tables (one per sheet) |
| Word | `.docx` | Semantic HTML |
| Images | `.png`, `.jpg`, `.gif`, `.webp` | Base64 embedded |
| HTML | `.html` | Sanitized, rendered |
| PDF | `.pdf` | Reference note (cannot embed) |
| Audio | `.mp3`, etc. | Reference note (unsupported) |

## Development Approach

This project follows **test-driven development**:

1. Write behavioral test first (in `tests/test_mbox_converter.py`)
2. Run test (should fail)
3. Implement feature in `src/`
4. Run test until passing
5. Commit test + implementation together

## Email Document Spec (Forensic/Legal)

Generated PDFs preserve complete email metadata:
- All headers: Date, From, To, Cc, Bcc, Subject, Message-ID, In-Reply-To, References
- Thread context with clear attribution
- Attachments listed with filename, type, size
- Each email starts on new page
- Professional formatting suitable for legal discovery

## Implementation Status

Core API and GUI complete (81 tests passing):
- [x] Project scaffolding and structure
- [x] Comprehensive design specification (DESIGN.md)
- [x] Test fixtures (simple.mbox, complex.mbox, takeout_fixture)
- [x] Core mbox parsing (`parse_mbox`, `merge_and_deduplicate`)
- [x] PDF generation with xhtml2pdf (`generate_pdf`)
- [x] Date grouping logic (`group_emails_by_date` - month/quarter/year)
- [x] Attachment rendering (text, CSV, images, references)
- [x] Email-to-HTML rendering (`render_email_to_html`)
- [x] High-level orchestration (`convert_mbox_to_pdfs` with progress callback)
- [x] Continuation headers for multi-page emails (`add_continuation_headers`, `merge_pdfs`)
- [x] GUI implementation (5-step wizard in `gui.py`)
- [ ] Error handling system (structured AttachmentError dialogs)
- [ ] CI/CD build pipeline

## Important Design Decisions

1. **xhtml2pdf over WeasyPrint**: Pure Python with no native dependencies, enabling easy cross-platform distribution via PyInstaller. Adequate CSS support for email-centric HTML rendering.
2. **Tkinter for GUI**: Stdlib, cross-platform, sufficient for wizard workflow
3. **No external network calls**: Privacy-first, all processing local
4. **API returns structured results**: ConversionResult dataclass, not exceptions for flow control
5. **Error dialogs from API**: AttachmentError carries context for user-friendly display

## References

- **DESIGN.md**: Complete requirements, architecture, dataclass specs, test matrix
- **README.md**: User-facing documentation and usage instructions
