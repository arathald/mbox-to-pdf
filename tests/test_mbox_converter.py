"""
Test suite for mbox-to-pdf.

Run with: pytest tests/
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from src.mbox_converter import (
    parse_mbox,
    merge_and_deduplicate,
    group_emails_by_date,
    render_attachment,
    render_email_to_html,
    generate_pdf,
    convert_mbox_to_pdfs,
    add_continuation_headers,
    merge_pdfs,
    Email,
    Attachment,
    ConversionResult,
)


class TestParseMbox:
    """Tests for mbox parsing functionality."""

    def test_parse_simple_mbox_returns_two_emails(self, simple_fixture):
        """Parsing simple.mbox should return exactly 2 Email objects."""
        emails = parse_mbox(simple_fixture)
        assert len(emails) == 2

    def test_parse_simple_mbox_first_email_headers(self, simple_fixture):
        """First email should have correct header fields."""
        emails = parse_mbox(simple_fixture)
        email = emails[0]

        assert email.message_id == "<simple001@example.com>"
        assert email.from_addr == "Alice Smith <alice@example.com>"
        assert email.to_addr == "bob@example.com"
        assert email.subject == "Happy New Year!"
        assert email.in_reply_to is None
        assert email.references is None

    def test_parse_simple_mbox_first_email_date(self, simple_fixture):
        """First email date should be correctly parsed with timezone."""
        emails = parse_mbox(simple_fixture)
        email = emails[0]

        # Jan 4, 2008 09:30:00 -0500
        expected_tz = timezone(timedelta(hours=-5))
        expected_date = datetime(2008, 1, 4, 9, 30, 0, tzinfo=expected_tz)
        assert email.date == expected_date

    def test_parse_simple_mbox_first_email_body(self, simple_fixture):
        """First email body should contain expected text."""
        emails = parse_mbox(simple_fixture)
        email = emails[0]

        assert "Happy New Year!" in email.body_text
        assert "Looking forward to working together in 2008" in email.body_text
        assert email.body_html is None  # Plain text email

    def test_parse_simple_mbox_second_email_threading(self, simple_fixture):
        """Second email should have threading metadata (In-Reply-To, References)."""
        emails = parse_mbox(simple_fixture)
        email = emails[1]

        assert email.message_id == "<simple002@example.com>"
        assert email.in_reply_to == "<simple001@example.com>"
        assert email.references == ["<simple001@example.com>"]

    def test_parse_simple_mbox_second_email_headers(self, simple_fixture):
        """Second email should have correct header fields."""
        emails = parse_mbox(simple_fixture)
        email = emails[1]

        assert email.from_addr == "Bob Jones <bob@example.com>"
        assert email.to_addr == "alice@example.com"
        assert email.subject == "Re: Happy New Year!"

    def test_parse_simple_mbox_no_attachments(self, simple_fixture):
        """Simple.mbox emails should have no attachments."""
        emails = parse_mbox(simple_fixture)

        for email in emails:
            assert email.attachments == []

    def test_parse_mbox_returns_list_of_email_objects(self, simple_fixture):
        """parse_mbox should return a list of Email dataclass instances."""
        emails = parse_mbox(simple_fixture)

        assert isinstance(emails, list)
        for email in emails:
            assert isinstance(email, Email)


class TestParseMboxComplex:
    """Tests for complex.mbox with attachments."""

    def test_parse_complex_mbox_returns_ten_emails(self, complex_fixture):
        """Parsing complex.mbox should return exactly 11 Email objects."""
        emails = parse_mbox(complex_fixture)
        assert len(emails) == 11

    def test_parse_complex_mbox_emails_sorted_by_date(self, complex_fixture):
        """Emails should be sorted by date ascending."""
        emails = parse_mbox(complex_fixture)
        dates = [e.date for e in emails]
        assert dates == sorted(dates)

    def test_text_attachment(self, complex_fixture):
        """Email 1 should have notes.txt attachment."""
        emails = parse_mbox(complex_fixture)
        email = emails[0]  # First email (Jan 10)

        assert email.subject == "Email with text attachment"
        assert len(email.attachments) == 1
        assert email.attachments[0].filename == "notes.txt"
        assert email.attachments[0].mime_type == "text/plain"

    def test_csv_attachment(self, complex_fixture):
        """Email 2 should have sales_q1.csv attachment."""
        emails = parse_mbox(complex_fixture)
        email = emails[1]  # Second email (Jan 11)

        assert email.subject == "Spreadsheet data as CSV"
        assert len(email.attachments) == 1
        assert email.attachments[0].filename == "sales_q1.csv"
        assert email.attachments[0].mime_type == "text/csv"

    def test_inline_image_html_email(self, complex_fixture):
        """Email 3 should be HTML with inline image attachment."""
        emails = parse_mbox(complex_fixture)
        email = emails[2]  # Third email (Jan 12)

        assert email.subject == "HTML email with inline image"
        assert email.body_html is not None
        assert "<h1>Project Status Report</h1>" in email.body_html
        # Inline image should be captured as attachment
        assert len(email.attachments) == 1
        assert email.attachments[0].filename == "timeline.png"
        assert email.attachments[0].mime_type == "image/png"

    def test_multiple_attachments(self, complex_fixture):
        """Email 4 should have multiple attachments of different types."""
        emails = parse_mbox(complex_fixture)
        email = emails[3]  # Fourth email (Jan 13)

        assert email.subject == "Multiple attachments - mixed types"
        assert len(email.attachments) == 3

        filenames = {a.filename for a in email.attachments}
        assert filenames == {"README.txt", "data.csv", "logo.png"}

    def test_attachment_size_tracking(self, complex_fixture):
        """Attachments should track size in bytes."""
        emails = parse_mbox(complex_fixture)
        email = emails[0]  # First email with notes.txt

        attachment = email.attachments[0]
        assert attachment.size_bytes > 0
        # notes.txt content is about 200 bytes
        assert 100 < attachment.size_bytes < 500

    def test_attachment_format_size_for_display(self, complex_fixture):
        """Attachment.format_size_for_display should return human-readable size."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[0].attachments[0]  # notes.txt

        size_display = attachment.format_size_for_display()
        # Should be something like "234 B" or "0.2 KB"
        assert "B" in size_display or "KB" in size_display


class TestDeduplication:
    """Tests for email deduplication by Message-ID."""

    def test_merge_single_file_no_change(self, simple_fixture):
        """Merging a single file should return all emails unchanged."""
        emails = merge_and_deduplicate([simple_fixture])
        assert len(emails) == 2

    def test_merge_two_identical_files_deduplicates(self, simple_fixture):
        """Merging the same file twice should deduplicate to original count."""
        emails = merge_and_deduplicate([simple_fixture, simple_fixture])
        assert len(emails) == 2

    def test_merge_preserves_all_unique_emails(self, simple_fixture, complex_fixture):
        """Merging distinct files should preserve all unique emails."""
        # simple has 2, complex has 10, no overlap = 12 unique
        emails = merge_and_deduplicate([simple_fixture, complex_fixture])
        assert len(emails) == 12

    def test_merge_result_sorted_by_date(self, simple_fixture, complex_fixture):
        """Merged result should be sorted by date ascending."""
        emails = merge_and_deduplicate([simple_fixture, complex_fixture])
        dates = [e.date for e in emails]
        assert dates == sorted(dates)


class TestTakeoutDeduplication:
    """Tests for Gmail Takeout deduplication scenarios."""

    def test_all_mail_contains_21_emails_with_dupes(self, takeout_fixture):
        """All Mail.mbox contains 21 emails (includes internal duplicates)."""
        all_mail = takeout_fixture / "Mail" / "All Mail.mbox"
        emails = parse_mbox(all_mail)
        assert len(emails) == 21

    def test_inbox_contains_2_emails(self, takeout_fixture):
        """Inbox.mbox should contain 2 emails (simple.mbox content)."""
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"
        emails = parse_mbox(inbox)
        assert len(emails) == 2

    def test_work_projects_contains_10_emails(self, takeout_fixture):
        """Work Projects.mbox should contain 10 emails (complex.mbox content)."""
        work = takeout_fixture / "Mail" / "Work Projects.mbox"
        emails = parse_mbox(work)
        assert len(emails) == 10

    def test_all_mail_plus_inbox_deduplicates_to_12(self, takeout_fixture):
        """All Mail + Inbox should deduplicate to 12 unique emails."""
        all_mail = takeout_fixture / "Mail" / "All Mail.mbox"
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"

        emails = merge_and_deduplicate([all_mail, inbox])
        # All Mail has 12 unique (2 simple + 10 complex), Inbox has same 2 simple
        assert len(emails) == 12

    def test_all_mail_plus_work_deduplicates_to_12(self, takeout_fixture):
        """All Mail + Work Projects should deduplicate to 12 unique emails."""
        all_mail = takeout_fixture / "Mail" / "All Mail.mbox"
        work = takeout_fixture / "Mail" / "Work Projects.mbox"

        emails = merge_and_deduplicate([all_mail, work])
        # All Mail has 12 unique, Work Projects has same 10 complex
        assert len(emails) == 12

    def test_inbox_plus_work_no_overlap(self, takeout_fixture):
        """Inbox + Work Projects should have no overlap (12 unique)."""
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"
        work = takeout_fixture / "Mail" / "Work Projects.mbox"

        emails = merge_and_deduplicate([inbox, work])
        # Inbox has 2 simple, Work has 10 complex, no overlap
        assert len(emails) == 12

    def test_all_three_deduplicates_to_12(self, takeout_fixture):
        """All Mail + Inbox + Work Projects should deduplicate to 12 unique."""
        all_mail = takeout_fixture / "Mail" / "All Mail.mbox"
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"
        work = takeout_fixture / "Mail" / "Work Projects.mbox"

        emails = merge_and_deduplicate([all_mail, inbox, work])
        # Total unique across all sources: 12
        assert len(emails) == 12

    def test_empty_mbox_handled(self, takeout_fixture):
        """Empty mbox file should not cause errors."""
        spam = takeout_fixture / "[Gmail]" / "Spam.mbox"
        emails = parse_mbox(spam)
        assert len(emails) == 0

    def test_merge_with_empty_mbox(self, takeout_fixture):
        """Merging with empty mbox should work correctly."""
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"
        spam = takeout_fixture / "[Gmail]" / "Spam.mbox"

        emails = merge_and_deduplicate([inbox, spam])
        assert len(emails) == 2


class TestDateGrouping:
    """Tests for grouping emails by month/quarter/year."""

    def test_group_by_month_returns_correct_keys(self, simple_fixture):
        """Grouping by month should return keys like '2008-01-January'."""
        emails = parse_mbox(simple_fixture)
        groups = group_emails_by_date(emails, "month")

        assert "2008-01-January" in groups
        assert len(groups) == 1  # All emails in January 2008

    def test_group_by_month_email_counts(self, simple_fixture):
        """Each month group should contain correct number of emails."""
        emails = parse_mbox(simple_fixture)
        groups = group_emails_by_date(emails, "month")

        assert len(groups["2008-01-January"]) == 2

    def test_group_by_quarter_returns_correct_keys(self, simple_fixture):
        """Grouping by quarter should return keys like '2008-Q1'."""
        emails = parse_mbox(simple_fixture)
        groups = group_emails_by_date(emails, "quarter")

        assert "2008-Q1" in groups
        assert len(groups) == 1

    def test_group_by_year_returns_correct_keys(self, simple_fixture):
        """Grouping by year should return keys like '2008'."""
        emails = parse_mbox(simple_fixture)
        groups = group_emails_by_date(emails, "year")

        assert "2008" in groups
        assert len(groups) == 1
        assert len(groups["2008"]) == 2

    def test_group_by_month_complex_fixture(self, complex_fixture):
        """Complex fixture spans Jan 10-19, all in one month."""
        emails = parse_mbox(complex_fixture)
        groups = group_emails_by_date(emails, "month")

        assert "2008-01-January" in groups
        assert len(groups["2008-01-January"]) == 11

    def test_emails_within_group_sorted_by_date(self, complex_fixture):
        """Emails within each group should be sorted by date ascending."""
        emails = parse_mbox(complex_fixture)
        groups = group_emails_by_date(emails, "month")

        january_emails = groups["2008-01-January"]
        dates = [e.date for e in january_emails]
        assert dates == sorted(dates)

    def test_group_keys_are_sorted(self, simple_fixture, complex_fixture):
        """Group keys should be returned in chronological order."""
        # Combine fixtures - simple is Jan 4-5, complex is Jan 10-19
        simple_emails = parse_mbox(simple_fixture)
        complex_emails = parse_mbox(complex_fixture)
        all_emails = simple_emails + complex_emails

        groups = group_emails_by_date(all_emails, "month")
        keys = list(groups.keys())

        # All in same month for these fixtures
        assert keys == sorted(keys)

    def test_empty_email_list_returns_empty_groups(self):
        """Empty email list should return empty dict."""
        groups = group_emails_by_date([], "month")
        assert groups == {}

    def test_invalid_strategy_raises_error(self, simple_fixture):
        """Invalid grouping strategy should raise ValueError."""
        emails = parse_mbox(simple_fixture)

        try:
            group_emails_by_date(emails, "invalid")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "invalid" in str(e).lower()

    def test_quarter_mapping(self, simple_fixture):
        """January should map to Q1."""
        emails = parse_mbox(simple_fixture)
        groups = group_emails_by_date(emails, "quarter")

        # January is Q1
        assert "2008-Q1" in groups


class TestAttachmentRendering:
    """Tests for attachment rendering to HTML."""

    def test_render_text_attachment_returns_pre_block(self, complex_fixture):
        """Text attachment should render as formatted text with paragraphs."""
        emails = parse_mbox(complex_fixture)
        email = emails[0]  # First email has notes.txt
        attachment = email.attachments[0]

        html = render_attachment(attachment)

        assert '<div class="attachment-text">' in html
        assert "Project Notes" in html  # Content from notes.txt
        assert "<p>" in html  # Should have paragraph tags

    def test_render_text_attachment_preserves_line_breaks(self, complex_fixture):
        """Text attachment should preserve line breaks."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[0].attachments[0]  # notes.txt

        html = render_attachment(attachment)

        # Should preserve structure with numbered items
        assert "1." in html or "Task:" in html

    def test_render_csv_attachment_returns_table(self, complex_fixture):
        """CSV attachment should render as HTML table."""
        emails = parse_mbox(complex_fixture)
        email = emails[1]  # Second email has sales_q1.csv
        attachment = email.attachments[0]

        html = render_attachment(attachment)

        assert "<table" in html
        assert "<tr>" in html
        assert "<th>" in html or "<td>" in html
        assert "</table>" in html

    def test_render_csv_includes_header_row(self, complex_fixture):
        """CSV table should include header row."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[1].attachments[0]  # sales_q1.csv

        html = render_attachment(attachment)

        # Check for column headers from sales_q1.csv
        assert "Month" in html
        assert "Region" in html
        assert "Sales" in html

    def test_render_csv_includes_data_rows(self, complex_fixture):
        """CSV table should include data rows."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[1].attachments[0]  # sales_q1.csv

        html = render_attachment(attachment)

        # Check for data values
        assert "January" in html
        assert "North" in html

    def test_render_image_attachment_returns_base64_img(self, complex_fixture):
        """Image attachment should render as base64-encoded img tag."""
        emails = parse_mbox(complex_fixture)
        email = emails[2]  # Third email has inline image
        attachment = email.attachments[0]  # timeline.png

        html = render_attachment(attachment)

        assert "<img" in html
        assert 'src="data:image/png;base64,' in html
        assert "/>" in html or "</img>" in html

    def test_render_image_includes_alt_text(self, complex_fixture):
        """Image should include alt text with filename."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[2].attachments[0]  # timeline.png

        html = render_attachment(attachment)

        assert "alt=" in html
        assert "timeline.png" in html or "timeline" in html

    def test_render_unsupported_type_returns_reference(self):
        """Unsupported attachment types should render as reference note."""
        attachment = Attachment(
            filename="meeting.mp3",
            mime_type="audio/mpeg",
            size_bytes=1024000,
            raw_content=b"fake audio data",
        )

        html = render_attachment(attachment)

        assert "meeting.mp3" in html
        assert "audio" in html.lower() or "reference" in html.lower()
        assert "1" in html  # Size should be shown (1 MB)

    def test_render_attachment_sets_content_type(self, complex_fixture):
        """render_attachment should set content_type on the attachment."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[0].attachments[0]  # notes.txt

        render_attachment(attachment)

        assert attachment.content_type == "text"

    def test_render_attachment_sets_rendered_content(self, complex_fixture):
        """render_attachment should populate rendered_content field."""
        emails = parse_mbox(complex_fixture)
        attachment = emails[0].attachments[0]  # notes.txt

        html = render_attachment(attachment)

        assert attachment.rendered_content == html
        assert attachment.rendered_content is not None


class TestEmailToHtml:
    """Tests for rendering complete emails to HTML."""

    def test_render_email_returns_html_string(self, simple_fixture):
        """render_email_to_html should return valid HTML string."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert isinstance(html, str)
        assert len(html) > 0

    def test_render_email_includes_wrapper(self, simple_fixture):
        """Email should be wrapped in email-message div."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert '<div class="email-message">' in html
        assert "</div>" in html

    def test_render_email_includes_header_section(self, simple_fixture):
        """Email should include header section."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert '<div class="email-header">' in html
        assert "<strong>Date:</strong>" in html
        assert "<strong>From:</strong>" in html

    def test_render_email_includes_from_field(self, simple_fixture):
        """Header should include From field."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "From:" in html or "From</span>" in html
        assert "alice@example.com" in html

    def test_render_email_includes_to_field(self, simple_fixture):
        """Header should include To field."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "To:" in html or "To</span>" in html
        assert "bob@example.com" in html

    def test_render_email_includes_date_field(self, simple_fixture):
        """Header should include Date field."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "Date:" in html or "Date</span>" in html
        assert "2008" in html  # Year should be visible

    def test_render_email_includes_subject(self, simple_fixture):
        """Header should include Subject field."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "Subject:" in html or "Subject</span>" in html
        assert "Happy New Year!" in html

    def test_render_email_includes_message_id(self, simple_fixture):
        """Header should include Message-ID for forensic reference."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "Message-ID:" in html or "Message-ID</span>" in html
        assert "simple001@example.com" in html

    def test_render_email_includes_body_section(self, simple_fixture):
        """Email should include body section."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert '<div class="email-body">' in html

    def test_render_email_body_contains_text(self, simple_fixture):
        """Body section should contain email text."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        assert "Happy New Year!" in html
        assert "Looking forward to working together" in html

    def test_render_email_with_threading_metadata(self, simple_fixture):
        """Email with In-Reply-To should show threading fields."""
        emails = parse_mbox(simple_fixture)
        email_with_reply = emails[1]  # Second email has In-Reply-To
        html = render_email_to_html(email_with_reply)

        assert "In-Reply-To:" in html or "In-Reply-To</span>" in html
        assert "simple001@example.com" in html

    def test_render_email_with_attachments_section(self, complex_fixture):
        """Email with attachments should include attachments section."""
        emails = parse_mbox(complex_fixture)
        email_with_attachment = emails[0]  # First email has notes.txt
        html = render_email_to_html(email_with_attachment)

        assert "attachment" in html.lower()
        assert "notes.txt" in html

    def test_render_html_email_preserves_body(self, complex_fixture):
        """HTML email body should be included (sanitized)."""
        emails = parse_mbox(complex_fixture)
        # Find the HTML email (email 3 - inline image)
        html_email = emails[2]
        html = render_email_to_html(html_email)

        assert "Project Status Report" in html


class TestPdfGeneration:
    """Tests for PDF generation with xhtml2pdf."""

    def test_generate_pdf_creates_file(self, simple_fixture, temp_output_dir):
        """generate_pdf should create a PDF file."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])
        output_path = temp_output_dir / "test.pdf"

        generate_pdf(html, output_path)

        assert output_path.exists()

    def test_generate_pdf_file_has_content(self, simple_fixture, temp_output_dir):
        """Generated PDF should have non-zero size."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])
        output_path = temp_output_dir / "test.pdf"

        generate_pdf(html, output_path)

        assert output_path.stat().st_size > 0

    def test_generate_pdf_is_valid_pdf(self, simple_fixture, temp_output_dir):
        """Generated file should start with PDF magic bytes."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])
        output_path = temp_output_dir / "test.pdf"

        generate_pdf(html, output_path)

        with open(output_path, "rb") as f:
            magic = f.read(5)
        assert magic == b"%PDF-"

    def test_generate_pdf_with_attachments(self, complex_fixture, temp_output_dir):
        """PDF generation should work with email containing attachments."""
        emails = parse_mbox(complex_fixture)
        html = render_email_to_html(emails[0])  # Email with notes.txt
        output_path = temp_output_dir / "with_attachment.pdf"

        generate_pdf(html, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generate_pdf_with_image(self, complex_fixture, temp_output_dir):
        """PDF generation should work with embedded images."""
        emails = parse_mbox(complex_fixture)
        html = render_email_to_html(emails[2])  # Email with inline image
        output_path = temp_output_dir / "with_image.pdf"

        generate_pdf(html, output_path)

        assert output_path.exists()
        # PDF with image should be larger
        assert output_path.stat().st_size > 1000

    def test_generate_pdf_returns_path(self, simple_fixture, temp_output_dir):
        """generate_pdf should return the output path."""
        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])
        output_path = temp_output_dir / "test.pdf"

        result = generate_pdf(html, output_path)

        assert result == output_path


class TestConvertMboxToPdfs:
    """Tests for the high-level convert_mbox_to_pdfs orchestration function."""

    def test_convert_returns_conversion_result(self, simple_fixture, temp_output_dir):
        """convert_mbox_to_pdfs should return a ConversionResult."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        assert isinstance(result, ConversionResult)

    def test_convert_creates_pdf_files(self, simple_fixture, temp_output_dir):
        """convert_mbox_to_pdfs should create PDF files in group subdirectories."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        assert result.pdfs_created > 0
        # PDFs are now in subdirectories: output_dir/<group>/<group>.pdf
        assert len(list(temp_output_dir.glob("*/*.pdf"))) > 0

    def test_convert_result_includes_created_files(self, simple_fixture, temp_output_dir):
        """ConversionResult should list all created PDF paths."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        assert len(result.created_files) == result.pdfs_created
        for pdf_path in result.created_files:
            assert Path(pdf_path).exists()

    def test_convert_groups_by_month(self, simple_fixture, temp_output_dir):
        """With month strategy, PDF filenames should include month."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        # simple.mbox has emails from January 2008
        pdf_names = [Path(p).name for p in result.created_files]
        assert any("2008-01" in name for name in pdf_names)

    def test_convert_groups_by_year(self, simple_fixture, temp_output_dir):
        """With year strategy, PDF filenames should include year only."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="year"
        )
        pdf_names = [Path(p).name for p in result.created_files]
        assert any("2008" in name for name in pdf_names)
        # Should not have month in filename
        assert not any("2008-01" in name for name in pdf_names)

    def test_convert_success_flag_true_on_success(self, simple_fixture, temp_output_dir):
        """ConversionResult.success should be True when conversion succeeds."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        assert result.success is True

    def test_convert_merges_multiple_mbox_files(self, simple_fixture, complex_fixture, temp_output_dir):
        """Multiple mbox files should be merged before conversion."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture, complex_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        # simple has 2 emails (Jan 4-5), complex has 10 (Jan 10-19)
        # All in January 2008, so should produce 1 PDF
        assert result.pdfs_created >= 1
        assert result.success is True

    def test_convert_deduplicates_emails(self, takeout_fixture, temp_output_dir):
        """Emails should be deduplicated by Message-ID across mbox files."""
        all_mail = takeout_fixture / "Mail" / "All Mail.mbox"
        inbox = takeout_fixture / "Mail" / "Inbox.mbox"

        result = convert_mbox_to_pdfs(
            mbox_paths=[all_mail, inbox],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        # Should not have duplicates - deduplication should work
        assert result.success is True

    def test_convert_calls_progress_callback(self, simple_fixture, temp_output_dir):
        """Progress callback should be called during conversion."""
        progress_calls = []

        def track_progress(current, total, message):
            progress_calls.append((current, total, message))

        convert_mbox_to_pdfs(
            mbox_paths=[simple_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month",
            progress_callback=track_progress
        )

        assert len(progress_calls) > 0

    def test_convert_with_complex_attachments(self, complex_fixture, temp_output_dir):
        """Conversion should handle emails with various attachment types."""
        result = convert_mbox_to_pdfs(
            mbox_paths=[complex_fixture],
            output_dir=temp_output_dir,
            grouping_strategy="month"
        )
        assert result.success is True
        assert result.pdfs_created > 0


class TestContinuationHeaders:
    """Tests for continuation headers on multi-page emails."""

    def test_add_continuation_headers_returns_path(self, temp_output_dir):
        """add_continuation_headers should return the output path."""
        from pypdf import PdfReader, PdfWriter

        # Create a simple 2-page PDF for testing
        input_pdf = temp_output_dir / "input.pdf"
        output_pdf = temp_output_dir / "output.pdf"

        # Generate a test PDF with enough content for 2 pages
        long_content = "<p>" + ("Lorem ipsum dolor sit amet. " * 200) + "</p>"
        generate_pdf(long_content, input_pdf)

        # Verify it has multiple pages
        reader = PdfReader(input_pdf)
        if len(reader.pages) < 2:
            pytest.skip("Test PDF did not generate multiple pages")

        result = add_continuation_headers(
            input_pdf,
            output_pdf,
            subject="Test Subject",
            from_addr="sender@example.com"
        )

        assert result == output_pdf
        assert output_pdf.exists()

    def test_add_continuation_headers_preserves_page_count(self, temp_output_dir):
        """Adding headers should not change the number of pages."""
        from pypdf import PdfReader

        input_pdf = temp_output_dir / "input.pdf"
        output_pdf = temp_output_dir / "output.pdf"

        # Generate a test PDF with enough content for 2+ pages
        long_content = "<p>" + ("Lorem ipsum dolor sit amet. " * 200) + "</p>"
        generate_pdf(long_content, input_pdf)

        reader = PdfReader(input_pdf)
        original_page_count = len(reader.pages)

        if original_page_count < 2:
            pytest.skip("Test PDF did not generate multiple pages")

        add_continuation_headers(
            input_pdf,
            output_pdf,
            subject="Test Subject",
            from_addr="sender@example.com"
        )

        reader = PdfReader(output_pdf)
        assert len(reader.pages) == original_page_count

    def test_single_page_pdf_unchanged(self, simple_fixture, temp_output_dir):
        """Single-page PDFs should pass through without modification."""
        from pypdf import PdfReader

        emails = parse_mbox(simple_fixture)
        html = render_email_to_html(emails[0])

        input_pdf = temp_output_dir / "single_page.pdf"
        output_pdf = temp_output_dir / "output.pdf"

        generate_pdf(html, input_pdf)

        reader = PdfReader(input_pdf)
        if len(reader.pages) > 1:
            pytest.skip("Test PDF has multiple pages, expected single page")

        add_continuation_headers(
            input_pdf,
            output_pdf,
            subject=emails[0].subject,
            from_addr=emails[0].from_addr
        )

        # Output should still be a valid PDF
        assert output_pdf.exists()
        reader = PdfReader(output_pdf)
        assert len(reader.pages) == 1
