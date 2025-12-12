# mbox-to-pdf

Convert Gmail Takeout mbox email files to PDF documents with an easy-to-use GUI application.

## Features

- **User-friendly GUI**: No command line required—just select folders and click
- **Multi-folder support**: Select which mbox files from your Takeout export to convert
- **Flexible grouping**: Organize PDFs by calendar month, quarter, or year
- **Privacy-first**: All processing happens locally on your machine
- **Error handling**: Clear error messages with copyable logs for troubleshooting
- **Cross-platform**: Available for Windows, macOS, and Linux

## Project Structure

```
mbox-to-pdf/
├── src/                    # Source code
│   ├── mbox_converter.py  # Core conversion logic
│   ├── gui.py             # Tkinter GUI
│   └── utils.py           # Utility functions
├── tests/                  # Test suite
├── sample_data/            # Sample mbox files for testing
├── build/                  # Build artifacts (CI/CD output)
└── requirements.txt        # Python dependencies
```

## Getting Started

### Development Setup

1. Clone the repo:
```bash
git clone <repo-url>
cd mbox-to-pdf
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

4. Run the application locally:
```bash
python src/gui.py
```

### Building Standalone Executables

Standalone executables are built via GitHub Actions CI/CD pipeline. They're available for:
- Windows (`.exe`)
- macOS (`.dmg`)
- Linux (AppImage)

See `.github/workflows/build.yml` for build configuration.

## Usage

1. Download your Gmail data from [Google Takeout](https://takeout.google.com)
2. Select "Mail (Gmail)" and request the export
3. Download and extract the exported zip file
4. Run the mbox-to-pdf application
5. Select the extracted Takeout folder
6. Choose which mbox files to convert
7. Select grouping preference (month, quarter, or year)
8. Choose output folder
9. Click "Convert"

## Development Roadmap

- [ ] Core mbox parsing + PDF generation
- [ ] Tkinter GUI with wizard-style flow
- [ ] Unit tests
- [ ] Error handling and logging
- [ ] GitHub Actions CI/CD build pipeline
- [ ] Windows installer support

## Security & Privacy

- **100% local processing**: No data sent to external servers
- **Standard libraries**: Uses only well-audited Python libraries (stdlib + weasyprint/reportlab)
- **Open source**: Full transparency—audit the code yourself
- **No tracking**: No analytics, telemetry, or data collection

## License

TBD

## Contributing

TBD
