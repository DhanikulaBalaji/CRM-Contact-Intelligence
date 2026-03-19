# Low-Level Design (LLD)

## CRM Contact Intelligence Platform

**Version:** 1.0
**Date:** 2025-03-24
**Author:** CRM Engineering Team

---

## 1. Contact Data Model

The `Contact` model is the central entity in the system. It represents a single sales contact with both user-provided fields and system-computed fields.

### 1.1 Field Definitions

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier for each contact record |
| `name` | String(255) | Required, NOT NULL | Full name of the contact person |
| `email` | String(255) | Required, NOT NULL, Unique, Indexed | Email address; used as the natural key for upsert operations |
| `phone` | String(50) | Optional, Nullable | Phone number in any format |
| `company` | String(255) | Required, NOT NULL, Indexed | Company or organization the contact belongs to |
| `status` | String(20) | Required, NOT NULL, Indexed | Contact lifecycle status; one of: `active`, `inactive`, `lead`, `churned` |
| `company_tier` | String(20) | Required, NOT NULL | Company classification; one of: `enterprise`, `mid-market`, `startup` |
| `last_contacted_date` | Date | Required, NOT NULL | Date of most recent interaction with the contact (format: YYYY-MM-DD) |
| `notes` | String(1000) | Optional, Nullable, Default: "" | Free-text notes about the contact |
| `score` | Float | Computed, Nullable, Default: 0.0 | Engagement/priority score (0.0–100.0), calculated by the scoring engine |
| `priority` | String(10) | Computed, Nullable, Default: "low", Indexed | Priority label derived from score: `high` (>70), `medium` (40–70), `low` (<40) |

### 1.2 SQLAlchemy Model Definition

```python
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    company_tier = Column(String(20), nullable=False)
    last_contacted_date = Column(Date, nullable=False)
    notes = Column(String(1000), nullable=True, default="")
    score = Column(Float, nullable=True, default=0.0)
    priority = Column(String(10), nullable=True, default="low", index=True)
```

### 1.3 Enumeration Values

**Status values:**
- `active` — Currently engaged contact with recent interactions
- `inactive` — Previously engaged contact with no recent activity
- `lead` — New prospective contact not yet converted
- `churned` — Contact who has left or cancelled

**Company tier values:**
- `enterprise` — Large organizations (>1000 employees or >$100M revenue)
- `mid-market` — Medium-sized organizations
- `startup` — Early-stage or small organizations

**Priority values (computed):**
- `high` — Score > 70; requires immediate attention
- `medium` — Score 40–70; follow up within the week
- `low` — Score < 40; low urgency, monitor periodically

---

## 2. Scoring Algorithm

### 2.1 Algorithm Overview

The scoring engine computes an engagement score from 0 to 100 for each contact. The score is a weighted sum of three independent factors, each capturing a different dimension of contact urgency.

### 2.2 Component Breakdown

#### Factor 1: Days Since Last Contact (Recency Score)

Contacts that have not been reached out to recently receive higher urgency scores.

| Condition | Score | Rationale |
|-----------|-------|-----------|
| `days_since > 90` | 30 | Severely overdue — high urgency |
| `60 < days_since ≤ 90` | 20 | Moderately overdue |
| `30 < days_since ≤ 60` | 10 | Slightly overdue |
| `days_since ≤ 30` | 5 | Recently contacted — low urgency |

#### Factor 2: Contact Status (Status Score)

Different lifecycle statuses carry different urgency weights.

| Status | Score | Rationale |
|--------|-------|-----------|
| `lead` | 25 | New leads should be engaged quickly |
| `inactive` | 20 | Re-engagement opportunity before churn |
| `active` | 15 | Maintain existing relationship |
| `churned` | 10 | Win-back potential but lower priority |

#### Factor 3: Company Tier (Tier Score)

Higher-value accounts receive higher urgency scores.

| Tier | Score | Rationale |
|------|-------|-----------|
| `enterprise` | 30 | Highest revenue potential |
| `mid-market` | 20 | Moderate revenue potential |
| `startup` | 10 | Lower immediate revenue but growth potential |

### 2.3 Pseudocode

```
function calculate_score(last_contacted_date, status, company_tier):
    score = 0
    reference_date = today()
    days_since = (reference_date - last_contacted_date).days

    # Factor 1: Recency
    if days_since > 90:
        score += 30
    elif days_since > 60:
        score += 20
    elif days_since > 30:
        score += 10
    else:
        score += 5

    # Factor 2: Status
    status_weights = {
        "lead": 25,
        "inactive": 20,
        "active": 15,
        "churned": 10
    }
    score += status_weights[status]

    # Factor 3: Company Tier
    tier_weights = {
        "enterprise": 30,
        "mid-market": 20,
        "startup": 10
    }
    score += tier_weights[company_tier]

    # Cap at 100
    score = min(score, 100)

    # Assign priority
    if score > 70:
        priority = "high"
    elif score >= 40:
        priority = "medium"
    else:
        priority = "low"

    return score, priority
```

### 2.4 Score Range Analysis

| Minimum Possible | Maximum Possible |
|-----------------|-----------------|
| 5 + 10 + 10 = 25 (low) | 30 + 25 + 30 = 85 (high) |

**Theoretical score ranges by priority:**
- **High (>70):** Requires at least two high-value factors. Example: enterprise + lead + 90+ days = 85
- **Medium (40–70):** Most common range for mid-tier contacts. Example: mid-market + inactive + 45 days = 50
- **Low (<40):** Recently contacted startups or active churned accounts. Example: startup + active + 10 days = 30

---

## 3. Database Schema

### 3.1 Table: `contacts`

```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    company VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    company_tier VARCHAR(20) NOT NULL,
    last_contacted_date DATE NOT NULL,
    notes VARCHAR(1000) DEFAULT '',
    score FLOAT DEFAULT 0.0,
    priority VARCHAR(10) DEFAULT 'low'
);
```

### 3.2 Indexes

| Index Name | Column(s) | Type | Purpose |
|-----------|-----------|------|---------|
| `ix_contacts_id` | `id` | Primary Key | Primary record lookup |
| `ix_contacts_email` | `email` | Unique | Upsert detection, duplicate prevention |
| `ix_contacts_status` | `status` | Non-unique | Status filter queries |
| `ix_contacts_company` | `company` | Non-unique | Company filter queries |
| `ix_contacts_priority` | `priority` | Non-unique | Priority filter queries |

### 3.3 Upsert Strategy

When importing contacts, the system uses email as the natural key:

1. For each contact in the CSV, query `SELECT * FROM contacts WHERE email = ?`
2. If a record exists: UPDATE all fields (name, phone, company, status, tier, date, notes, score, priority)
3. If no record exists: INSERT a new row
4. Commit the transaction after processing all contacts

This ensures idempotent imports — uploading the same CSV twice produces the same result.

---

## 4. Function-Level Design

### 4.1 Scoring Engine (`app/scorer.py`)

#### `calculate_days_score(days_since_contact: int) -> int`
- Input: Number of days since last contact (non-negative integer)
- Output: Recency score component (5, 10, 20, or 30)
- Pure function, no side effects

#### `calculate_status_score(status: str) -> int`
- Input: Contact status string (case-insensitive)
- Output: Status score component (0–25)
- Returns 0 for unknown status values

#### `calculate_tier_score(company_tier: str) -> int`
- Input: Company tier string (case-insensitive)
- Output: Tier score component (0–30)
- Returns 0 for unknown tier values

#### `calculate_score(last_contacted_date, status, company_tier, reference_date=None) -> tuple[float, str]`
- Input: Contact attributes and optional reference date for testing
- Output: Tuple of (score, priority)
- Delegates to component functions, sums, caps at 100, assigns priority

#### `score_contacts(contacts: list[dict], reference_date=None) -> list[dict]`
- Input: List of contact dictionaries with required keys
- Output: New list with `score` and `priority` fields added
- Does not mutate input; creates copies

#### `get_score_breakdown(last_contacted_date, status, company_tier, reference_date=None) -> dict`
- Input: Same as calculate_score
- Output: Dict with all component scores and metadata
- Used for detailed score explanations in the UI

### 4.2 Ingestion Module (`app/ingestion.py`)

#### `validate_email(email: str) -> bool`
- Regex-based email format validation
- Pattern: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`

#### `validate_date(date_str: str) -> bool`
- Checks if string matches YYYY-MM-DD format
- Uses `datetime.strptime` for validation

#### `ingest_csv(file_path_or_buffer) -> tuple[pd.DataFrame, ValidationResult]`
- Reads CSV into DataFrame
- Validates required columns exist
- Iterates rows to validate individual fields
- Collects errors per row with row numbers (1-indexed + header offset)
- Removes invalid rows from output DataFrame
- Detects and removes duplicate emails (keeps first)
- Returns clean DataFrame and ValidationResult object

#### `ValidationResult` class
- `errors: list[str]` — Validation error messages
- `warnings: list[str]` — Non-fatal warnings (e.g., duplicates removed)
- `valid_rows: int` — Count of valid rows
- `invalid_rows: int` — Count of invalid rows
- `is_valid: bool` — Property; True if no errors and no invalid rows

### 4.3 Analytics Module (`app/analytics.py`)

#### `get_priority_distribution(df) -> pd.DataFrame`
- Groups contacts by priority, returns value counts

#### `get_status_breakdown(df) -> pd.DataFrame`
- Groups contacts by status, returns value counts

#### `get_contacts_by_company(df) -> pd.DataFrame`
- Groups contacts by company, returns value counts

#### `get_score_distribution(df) -> pd.DataFrame`
- Returns the Score column for histogram plotting

#### `get_summary_stats(df) -> dict`
- Returns dict with: total_contacts, avg_score, high_priority, medium_priority, low_priority

### 4.4 Exporter Module (`app/exporter.py`)

#### `export_contacts_to_csv(contacts_df) -> bytes`
- Converts DataFrame to CSV byte string using BytesIO buffer

#### `export_filtered_contacts(contacts_df, filename) -> tuple[bytes, str]`
- Wrapper that returns CSV bytes and the suggested filename

---

## 5. Data Validation Rules

### 5.1 Required Fields

The following fields must be present and non-empty in every CSV row:

| Field | Validation |
|-------|-----------|
| `name` | Non-empty string |
| `email` | Non-empty, valid email format |
| `company` | Non-empty string |
| `status` | One of: active, inactive, lead, churned (case-insensitive) |
| `company_tier` | One of: enterprise, mid-market, startup (case-insensitive) |
| `last_contacted_date` | Valid date in YYYY-MM-DD format |

### 5.2 Optional Fields

| Field | Default if Missing |
|-------|-------------------|
| `phone` | Empty string |
| `notes` | Empty string |

### 5.3 Computed Fields (Not in CSV)

| Field | Computation |
|-------|------------|
| `score` | Calculated by scoring engine (0.0–100.0) |
| `priority` | Derived from score: high (>70), medium (40–70), low (<40) |

### 5.4 Email Validation

- Must match regex: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`
- Must be unique across the dataset (duplicates trigger a warning and are removed)
- Used as the natural key for database upsert operations

### 5.5 Date Validation

- Must match format: `YYYY-MM-DD` (e.g., 2025-01-15)
- Validated using `datetime.strptime(date_str, "%Y-%m-%d")`
- Must represent a valid calendar date

---

## 6. Error Handling Approach

### 6.1 Ingestion Errors

| Error Type | Handling Strategy | User Impact |
|-----------|------------------|-------------|
| File unreadable | Raise `IngestionError` | Error message in sidebar |
| Empty CSV | Raise `IngestionError` | Error message in sidebar |
| Missing required columns | Raise `IngestionError` | Error message listing missing columns |
| Missing required field in row | Add to `ValidationResult.errors` | Warning with row number and field name |
| Invalid email format | Add to `ValidationResult.errors` | Warning with row number and invalid value |
| Invalid status value | Add to `ValidationResult.errors` | Warning with row number and invalid value |
| Invalid company_tier | Add to `ValidationResult.errors` | Warning with row number and invalid value |
| Invalid date format | Add to `ValidationResult.errors` | Warning with row number and invalid value |
| Duplicate email | Add to `ValidationResult.warnings` | Info message listing removed duplicates |

### 6.2 Error Propagation

- **Fatal errors** (IngestionError): Prevent any data from being processed. Display error in sidebar.
- **Row-level errors**: Invalid rows are excluded from the valid DataFrame. Valid rows are still processed.
- **Warnings**: Non-fatal issues (like duplicate removal) are displayed as info messages.

### 6.3 Database Errors

- SQLAlchemy session errors are caught and rolled back
- Session is always closed in a `finally` block to prevent connection leaks
- Unique constraint violations are handled by the upsert logic (check-then-update pattern)

### 6.4 Scoring Errors

- Unknown status values receive a score of 0 (graceful degradation)
- Unknown tier values receive a score of 0
- Scores are capped at 100 to prevent overflow from future rule additions
