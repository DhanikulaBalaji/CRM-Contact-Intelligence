"""CSV ingestion module handling parsing, validation, and deduplication of contact data."""

import re
from datetime import datetime

import pandas as pd

REQUIRED_COLUMNS = ["name", "email", "company", "status", "company_tier", "last_contacted_date"]
VALID_STATUSES = {"active", "inactive", "lead", "churned"}
VALID_TIERS = {"enterprise", "mid-market", "startup"}
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class IngestionError(Exception):
    pass


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.valid_rows: int = 0
        self.invalid_rows: int = 0

    @property
    def is_valid(self) -> bool:
        return self.invalid_rows == 0 and len(self.errors) == 0


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(str(email)))


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(str(date_str), "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def ingest_csv(file_path_or_buffer) -> tuple[pd.DataFrame, ValidationResult]:
    result = ValidationResult()

    try:
        df = pd.read_csv(file_path_or_buffer)
    except Exception as e:
        raise IngestionError(f"Failed to read CSV: {str(e)}")

    if df.empty:
        raise IngestionError("CSV file is empty")

    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise IngestionError(f"Missing required columns: {', '.join(missing_cols)}")

    row_errors = []
    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed + header

        for col in REQUIRED_COLUMNS:
            if pd.isna(row.get(col)) or str(row.get(col)).strip() == "":
                row_errors.append((idx, f"Row {row_num}: Missing required field '{col}'"))

        if not pd.isna(row.get("email")) and not validate_email(str(row["email"])):
            row_errors.append((idx, f"Row {row_num}: Invalid email format '{row['email']}'"))

        if not pd.isna(row.get("status")) and str(row["status"]).lower() not in VALID_STATUSES:
            row_errors.append((idx, f"Row {row_num}: Invalid status '{row['status']}'"))

        if not pd.isna(row.get("company_tier")) and str(row["company_tier"]).lower() not in VALID_TIERS:
            row_errors.append((idx, f"Row {row_num}: Invalid company_tier '{row['company_tier']}'"))

        if not pd.isna(row.get("last_contacted_date")) and not validate_date(str(row["last_contacted_date"])):
            row_errors.append((idx, f"Row {row_num}: Invalid date format '{row['last_contacted_date']}'"))

    invalid_indices = set(idx for idx, _ in row_errors)
    result.errors = [msg for _, msg in row_errors]
    result.invalid_rows = len(invalid_indices)
    result.valid_rows = len(df) - len(invalid_indices)

    valid_df = df.drop(index=list(invalid_indices))

    duplicates = valid_df[valid_df.duplicated(subset=["email"], keep="first")]
    if not duplicates.empty:
        dup_emails = duplicates["email"].tolist()
        result.warnings.append(f"Duplicate emails found and removed: {', '.join(dup_emails)}")
        valid_df = valid_df.drop_duplicates(subset=["email"], keep="first")

    return valid_df, result
