# mbox-to-pdf

**Convert your Gmail emails to PDF files for safekeeping, legal records, or printing.**

A simple desktop application that takes your Gmail Takeout export and converts it to professional PDF documents. No technical knowledge required.

## What It Does

- Converts Gmail Takeout exports (`.mbox` files) to PDF documents
- Groups emails by month, quarter, or year into separate PDF files
- Preserves all email details: sender, recipients, dates, subject, and attachments
- Handles attachments: text files, images, spreadsheets, and documents are included in the PDFs
- Works completely offline — your emails never leave your computer

## Download

Download the latest version for your operating system:

| Operating System | Download |
|-----------------|----------|
| Windows | [mbox-to-pdf-windows.exe](https://github.com/YOUR_USERNAME/mbox-to-pdf/releases/latest) |
| macOS | [mbox-to-pdf-macos](https://github.com/YOUR_USERNAME/mbox-to-pdf/releases/latest) |
| Linux | [mbox-to-pdf-linux](https://github.com/YOUR_USERNAME/mbox-to-pdf/releases/latest) |

## How to Use

### Step 1: Export Your Gmail

1. Go to [Google Takeout](https://takeout.google.com)
2. Click "Deselect all" at the top
3. Scroll down and check only "Mail"
4. Click "Next step" and then "Create export"
5. Wait for Google to email you when it's ready (can take hours or days)
6. Download and unzip the export file

### Step 2: Run mbox-to-pdf

1. Open the mbox-to-pdf application
2. **Select Folder**: Browse to your unzipped Takeout folder
3. **Select Files**: Check which email folders you want to convert
4. **Choose Grouping**: Pick how to organize your PDFs (by month, quarter, or year)
5. **Choose Output**: Pick where to save your PDF files
6. **Convert**: Click Convert and wait for it to finish

### Step 3: View Your PDFs

Your emails are now saved as PDF files in the folder you chose. Each PDF contains all emails from that time period, with attachments included.

## Privacy & Security

- **100% offline**: Your emails are never uploaded anywhere
- **Open source**: You can inspect exactly what the code does
- **No tracking**: No analytics, no telemetry, no data collection

## Common Questions

**Q: How long does conversion take?**
A few seconds to a few minutes, depending on how many emails you have.

**Q: What happens to attachments I can't open, like ZIP files?**
They're listed in the PDF with their filename and size, but the contents aren't shown.

**Q: Can I convert just some emails?**
Yes! In Step 2, you can uncheck any folders you don't want to include.

**Q: The app won't open on my Mac. What do I do?**
Right-click the app and choose "Open" to bypass the security warning for unsigned apps.

## Suitable For

- Legal document discovery
- Financial records retention
- Email archiving for compliance
- Personal email backup
- Estate planning documentation

---

## For Developers

### Setup

```bash
# Clone and set up
git clone https://github.com/YOUR_USERNAME/mbox-to-pdf.git
cd mbox-to-pdf
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run tests
PYTHONPATH=. pytest tests/

# Run the app
PYTHONPATH=. python src/gui.py
```

### Build Executable

```bash
pyinstaller --onefile --windowed --name "mbox-to-pdf" src/gui.py
# Output: dist/mbox-to-pdf
```

### Project Structure

```
src/
├── mbox_converter.py  # Core conversion logic
├── gui.py             # Tkinter GUI
└── error_handling.py  # Error classification
tests/                 # Test suite (111 tests)
sample_data/           # Test fixtures
```

## License

MIT License - see [LICENSE](LICENSE) for details.
