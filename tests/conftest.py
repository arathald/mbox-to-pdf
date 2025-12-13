"""
Pytest fixtures for mbox-to-pdf test suite.

These fixtures provide access to test data files in sample_data/ directory.
"""

from pathlib import Path
import pytest


@pytest.fixture
def simple_fixture():
    """
    Path to sample_data/simple.mbox for basic parsing tests.

    Location: mbox-to-pdf/sample_data/simple.mbox
    Contains: 2 plain text emails (Jan 4-5, 2008)
    - Email 1: "Happy New Year!" from alice@example.com
    - Email 2: "Re: Happy New Year!" reply from bob@example.com (has In-Reply-To)
    """
    return Path(__file__).parent.parent / "sample_data" / "simple.mbox"


@pytest.fixture
def complex_fixture():
    """
    Path to sample_data/complex.mbox for comprehensive tests.

    Location: mbox-to-pdf/sample_data/complex.mbox
    Contains: 10 emails with various attachment types (Jan 10-19, 2008)

    Emails:
    1. Text attachment - notes.txt
    2. CSV attachment - sales_q1.csv
    3. Inline image - multipart/related with embedded PNG
    4. Mixed attachments - README.txt, data.csv, logo.png
    5. Non-UTF8 encoding - ISO-8859-1 with special characters
    6. HTML attachment - report.html
    7. Excel attachment - budget_2008.xlsx
    8. Word attachment - project_proposal.docx
    9. PDF attachment - financial_report_q1.pdf
    10. Unsupported file - meeting-recording.mp3 (for error dialog testing)
    """
    return Path(__file__).parent.parent / "sample_data" / "complex.mbox"


@pytest.fixture
def takeout_fixture():
    """
    Path to sample_data/takeout_fixture/ directory for multi-file tests.

    Location: mbox-to-pdf/sample_data/takeout_fixture/
    Structure: Realistic Gmail Takeout export layout

    Contains:
      - Mail/All Mail.mbox (21 records, 12 unique emails - simple + complex with internal dupes)
      - Mail/Inbox.mbox (2 emails - simple.mbox content, dupes of All Mail)
      - Mail/Work Projects.mbox (10 emails - complex.mbox content, dupes of All Mail)
      - Mail/Drafts.mbox (6 emails - subset)
      - Mail/Sent Mail.mbox (6 emails - subset)
      - Mail/Project Notes.mbox (6 emails - custom label)
      - [Gmail]/Important.mbox (4 emails - Gmail system label)
      - [Gmail]/Spam.mbox (0 emails - empty file handling test)

    Email content:
      - simple.mbox emails (Jan 4-5): plain text, threading metadata (2 unique)
      - complex.mbox emails (Jan 10-19): all attachment types (10 unique)
      - Total unique emails: 12

    Deduplication scenarios (all resolve to 12 unique):
      - All Mail alone → 12 unique (internal dupes removed)
      - All Mail + Inbox → 12 unique (Inbox dupes All Mail's simple emails)
      - All Mail + Work Projects → 12 unique (Work dupes All Mail's complex emails)
      - Inbox + Work Projects → 12 unique (no overlap between them)
      - All three → 12 unique

    Test scenarios:
    - Folder selection (Step 1)
    - Multiple .mbox file discovery (Step 2) - discovers 8 files
    - Partial selection of files
    - Multi-file merging before grouping
    - **Deduplication**: Multiple overlap scenarios between folders
    - Directory traversal and recursive file discovery
    - Empty mbox file handling (Spam.mbox)
    """
    return Path(__file__).parent.parent / "sample_data" / "takeout_fixture"


@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Temporary directory for PDF output during tests.

    Created fresh for each test, automatically cleaned up after.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
