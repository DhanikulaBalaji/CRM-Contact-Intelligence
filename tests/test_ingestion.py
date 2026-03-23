import io
import pytest
import pandas as pd
from app.ingestion import ingest_csv, IngestionError, validate_email, validate_date


VALID_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,alice@test.com,555-0101,TestCorp,active,enterprise,2025-01-15,Notes here
Bob Smith,bob@test.com,555-0102,OtherCorp,lead,mid-market,2024-12-01,More notes
"""

MISSING_COLUMNS_CSV = """name,phone,company,status
Alice Johnson,555-0101,TestCorp,active
"""

EMPTY_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
"""

MISSING_FIELDS_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
,alice@test.com,555-0101,TestCorp,active,enterprise,2025-01-15,Notes
Bob Smith,bob@test.com,555-0102,,lead,mid-market,2024-12-01,Notes
"""

DUPLICATE_EMAILS_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,alice@test.com,555-0101,TestCorp,active,enterprise,2025-01-15,First
Alice Clone,alice@test.com,555-0199,OtherCorp,lead,mid-market,2024-12-01,Duplicate
Bob Smith,bob@test.com,555-0102,TestCorp,lead,startup,2025-02-01,Unique
"""

INVALID_EMAIL_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,not-an-email,555-0101,TestCorp,active,enterprise,2025-01-15,Notes
"""

INVALID_DATE_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,alice@test.com,555-0101,TestCorp,active,enterprise,03/15/2025,Notes
"""

INVALID_STATUS_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,alice@test.com,555-0101,TestCorp,unknown,enterprise,2025-01-15,Notes
"""

INVALID_TIER_CSV = """name,email,phone,company,status,company_tier,last_contacted_date,notes
Alice Johnson,alice@test.com,555-0101,TestCorp,active,mega,2025-01-15,Notes
"""


class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_valid_email_with_dots(self):
        assert validate_email("first.last@domain.co.uk") is True

    def test_valid_email_with_plus(self):
        assert validate_email("user+tag@example.com") is True

    def test_invalid_email_no_at(self):
        assert validate_email("not-an-email") is False

    def test_invalid_email_no_domain(self):
        assert validate_email("user@") is False

    def test_empty_email(self):
        assert validate_email("") is False


class TestValidateDate:
    def test_valid_date(self):
        assert validate_date("2025-01-15") is True

    def test_invalid_date_format(self):
        assert validate_date("03/15/2025") is False

    def test_invalid_date_value(self):
        assert validate_date("2025-13-45") is False

    def test_empty_string(self):
        assert validate_date("") is False

    def test_non_date_string(self):
        assert validate_date("not-a-date") is False


class TestIngestCSVValid:
    def test_valid_csv(self):
        df, result = ingest_csv(io.StringIO(VALID_CSV))
        assert len(df) == 2
        assert result.is_valid
        assert result.valid_rows == 2
        assert result.invalid_rows == 0
        assert len(result.errors) == 0

    def test_valid_csv_has_expected_columns(self):
        df, _ = ingest_csv(io.StringIO(VALID_CSV))
        assert "name" in df.columns
        assert "email" in df.columns
        assert "company" in df.columns
        assert "status" in df.columns
        assert "company_tier" in df.columns
        assert "last_contacted_date" in df.columns


class TestIngestCSVErrors:
    def test_missing_required_columns(self):
        with pytest.raises(IngestionError, match="Missing required columns"):
            ingest_csv(io.StringIO(MISSING_COLUMNS_CSV))

    def test_empty_csv(self):
        with pytest.raises(IngestionError, match="empty"):
            ingest_csv(io.StringIO(EMPTY_CSV))

    def test_missing_field_values(self):
        df, result = ingest_csv(io.StringIO(MISSING_FIELDS_CSV))
        assert result.invalid_rows == 2
        assert len(result.errors) > 0
        assert any("Missing required field" in err for err in result.errors)

    def test_duplicate_emails(self):
        df, result = ingest_csv(io.StringIO(DUPLICATE_EMAILS_CSV))
        assert len(df) == 2  # first alice + bob, duplicate alice removed
        assert len(result.warnings) > 0
        assert any("Duplicate" in warn for warn in result.warnings)

    def test_invalid_email_format(self):
        df, result = ingest_csv(io.StringIO(INVALID_EMAIL_CSV))
        assert result.invalid_rows == 1
        assert any("Invalid email format" in err for err in result.errors)

    def test_invalid_date_format(self):
        df, result = ingest_csv(io.StringIO(INVALID_DATE_CSV))
        assert result.invalid_rows == 1
        assert any("Invalid date format" in err for err in result.errors)

    def test_invalid_status(self):
        df, result = ingest_csv(io.StringIO(INVALID_STATUS_CSV))
        assert result.invalid_rows == 1
        assert any("Invalid status" in err for err in result.errors)

    def test_invalid_company_tier(self):
        df, result = ingest_csv(io.StringIO(INVALID_TIER_CSV))
        assert result.invalid_rows == 1
        assert any("Invalid company_tier" in err for err in result.errors)

    def test_unreadable_input(self):
        with pytest.raises(IngestionError, match="Failed to read CSV"):
            ingest_csv(12345)
