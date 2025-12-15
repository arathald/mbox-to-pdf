# mbox-to-pdf

**Convert your Gmail emails to PDF files for safekeeping, legal records, or printing.**

A simple desktop application that takes your Gmail Takeout export and converts it to professional PDF documents. No technical knowledge required.

## What It Does

- Converts Gmail Takeout exports (`.mbox` files) to PDF documents
- Groups emails by month, quarter, or year into separate PDF files
- Preserves all email details: sender, recipients, dates, subject, and complete headers
- Saves attachments in organized folders alongside the PDFs (by date)
- Professional formatting suitable for legal discovery, financial records, or archiving
- Works completely offline — your emails never leave your computer

## Features

- **Organized Output**: Emails grouped by time period with attachments organized by date
- **Complete Headers**: All email metadata preserved for forensic completeness
- **Page Headers**: Every page shows the email subject, sender, date, and page number (helpful for printed documents)
- **Multiple Attachments**: Text files, images, spreadsheets, and documents all saved with the PDFs
- **Works Everywhere**: Windows, macOS, and Linux

## Download

Download the latest version for your operating system from the [Releases page](https://github.com/arathald/mbox-to-pdf/releases):

- **Windows**: `mbox-to-pdf.exe`
- **macOS**: `mbox-to-pdf` (universal binary, Intel + Apple Silicon)
- **Linux**: `mbox-to-pdf`

## How to Use

### Step 1: Export Your Gmail

1. Go to [Google Takeout](https://takeout.google.com)
2. Click "Deselect all" at the top
3. Scroll down and check only **Mail**
4. Click "Next step" and then "Create export"
5. Google will email you when it's ready (can take hours or days)
6. Download and unzip the export file

You'll see a folder structure like:
```
Takeout/
└── Mail/
    ├── All Mail.mbox
    ├── Inbox.mbox
    ├── Sent Mail.mbox
    └── ...
```

### Step 2: Run mbox-to-pdf

1. **Open the app**: Double-click `mbox-to-pdf`
2. **Select Folder**: Browse to your unzipped Takeout folder (choose the folder containing the `.mbox` files)
3. **Select Files**: Check which email folders you want to convert
4. **Choose Grouping**: Pick how to organize your PDFs:
   - **Month**: One PDF per month (e.g., `2024-01-January.pdf`)
   - **Quarter**: One PDF per quarter (e.g., `2024-Q1.pdf`)
   - **Year**: One PDF per year (e.g., `2024.pdf`)
5. **Choose Output**: Pick where to save your PDF files
6. **Convert**: Click "Convert" and wait for it to finish

### Step 3: View Your PDFs

Your emails are now organized in your output folder. Each group folder contains:

```
2024-Q1/
├── 2024-Q1.pdf                    ← The PDF with all emails from the period
└── attachments/
    ├── 2024-01-15/                ← Emails from January 15
    │   ├── invoice.pdf
    │   └── receipt.xlsx
    ├── 2024-02-03/                ← Emails from February 3
    │   └── contract.docx
    └── 2024-03-20/
        └── notes.txt
```

**To find an attachment**:
1. Open the PDF and look for the email you want
2. The PDF lists each attachment with its filename and location (e.g., "attachments/2024-01-15/invoice.pdf")
3. Go to that folder and open the file

### Step 4 (Optional): Archive Everything

The entire `2024-Q1/` folder (PDF + all attachments) can be zipped together for storage or sharing. When unzipped, everything works the same way.

## Privacy & Security

- **100% offline**: Your emails are never uploaded anywhere
- **Open source**: You can inspect exactly what the code does at [GitHub](https://github.com/arathald/mbox-to-pdf)
- **No tracking**: No analytics, no telemetry, no data collection
- **All dependencies up-to-date**: Regular security audits ensure no vulnerabilities

## Common Questions

**Q: How long does conversion take?**
A: A few seconds to a few minutes, depending on how many emails you have.

**Q: What about unsupported attachments (ZIP files, executables, etc.)?**
A: They're saved to the attachments folder so you can access them directly. The PDF lists them with their filename and size.

**Q: Can I convert just some emails?**
A: Yes! In Step 2, uncheck any folders you don't want to include.

**Q: The app won't open on my Mac. What do I do?**
A: Right-click the app and choose "Open" to bypass the security warning for unsigned apps.

**Q: Can I move the PDF around without breaking the attachment links?**
A: Yes! Keep the PDF and `attachments/` folder in the same directory, and everything works. You can move the entire group folder wherever you want.

**Q: How do I print the emails?**
A: Open the PDF in your PDF reader and print normally. Page headers show the subject, sender, date, and page number, so printed documents are clearly labeled.

**Q: What if I have thousands of emails?**
A: It works fine. The grouping option lets you split them into manageable chunks (by month, quarter, or year).

## Suitable For

- **Legal document discovery**: Complete headers and forensic metadata preserved
- **Financial records retention**: Organized by date for easy auditing
- **Email archiving for compliance**: Professional formatting, no proprietary formats
- **Personal email backup**: Offline storage independent of cloud services
- **Estate planning**: Permanent record of digital correspondence
- **Printing and filing**: Page headers make printed documents clearly labeled and organized

## Troubleshooting

**"No emails found"**: Make sure you selected the folder containing the `.mbox` files (e.g., the `Mail/` folder from Takeout, not the `Takeout/` root folder).

**"Conversion failed"**: Check that you have permission to write to the output folder.

**"App won't start"**: On Linux, try running from terminal: `./mbox-to-pdf` in the directory where you downloaded the app.

**Something else?**: Check the application logs (shown when you run the app).

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
