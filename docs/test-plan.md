# Test Plan

## CRM Contact Intelligence Platform

**Version:** 1.0
**Date:** 2025-03-24
**Author:** CRM QA Team

---

## 1. Test Objectives

The primary objectives of this test plan are:

1. **Verify correctness** of the scoring algorithm across all input combinations and boundary conditions.
2. **Validate data ingestion** to ensure CSV parsing, validation, and deduplication work as specified.
3. **Confirm analytics accuracy** by verifying that aggregation functions produce correct counts and statistics.
4. **Ensure export functionality** generates valid CSV output matching the filtered dataset.
5. **Validate persistence** to confirm that contact data and scores survive application restarts.
6. **End-to-end verification** that the complete workflow from CSV upload to dashboard display operates correctly.

---

## 2. Test Scope

### In Scope

- Unit tests for all scoring component functions
- Unit tests for ingestion validation logic
- Unit tests for analytics aggregation functions
- Functional tests for CSV export
- Edge case tests (empty data, boundary scores, invalid inputs)
- Integration tests for the upload-to-dashboard pipeline

### Out of Scope

- Streamlit UI visual/interaction testing (manual verification)
- Performance/load testing beyond basic benchmarks
- Security testing (authentication, authorization)
- Cross-browser compatibility testing

---

## 3. Test Environment

- **Language:** Python 3.11+
- **Framework:** pytest 8.3.3
- **Coverage:** pytest-cov 5.0.0
- **Coverage Target:** 80% minimum line coverage across `app/` package
- **CI Platform:** GitHub Actions (ubuntu-latest, Python 3.11 and 3.12)

---

## 4. Test Strategy

### 4.1 Unit Testing

Each module is tested in isolation with controlled inputs. External dependencies (database, file system) are mocked or replaced with in-memory alternatives (e.g., `io.StringIO` for CSV buffers).

### 4.2 Boundary Testing

Score thresholds (39/40 and 70/71) and all enumeration values are explicitly tested to ensure correct priority assignment at boundaries.

### 4.3 Negative Testing

Invalid inputs (missing fields, bad formats, unknown enum values) are tested to verify graceful error handling and correct error messages.

### 4.4 Integration Testing

The full pipeline from CSV ingestion through scoring to analytics is tested to verify correct data flow between modules.

---

## 5. Test Cases

### 5.1 Scoring Engine Tests

| Test ID | Description | Input | Expected Output | Type |
|---------|------------|-------|-----------------|------|
| TC-001 | Days score: >90 days since contact | `days_since_contact = 100` | `days_score = 30` | Unit |
| TC-002 | Days score: 61-90 days since contact | `days_since_contact = 75` | `days_score = 20` | Unit |
| TC-003 | Days score: 31-60 days since contact | `days_since_contact = 45` | `days_score = 10` | Unit |
| TC-004 | Days score: ≤30 days since contact | `days_since_contact = 15` | `days_score = 5` | Unit |
| TC-005 | Status score: all valid statuses | `status = "lead"` / `"inactive"` / `"active"` / `"churned"` | `25` / `20` / `15` / `10` | Unit |
| TC-006 | Tier score: all valid tiers | `tier = "enterprise"` / `"mid-market"` / `"startup"` | `30` / `20` / `10` | Unit |
| TC-007 | Combined score: enterprise + lead + 100 days | `last_contacted = 100 days ago, status = "lead", tier = "enterprise"` | `score = 85, priority = "high"` | Unit |
| TC-008 | Combined score: startup + active + 10 days | `last_contacted = 10 days ago, status = "active", tier = "startup"` | `score = 30, priority = "low"` | Unit |
| TC-009 | Boundary: score exactly 70 | Inputs producing exactly 70 | `priority = "medium"` | Boundary |
| TC-010 | Boundary: score exactly 71 | Inputs producing 71 | `priority = "high"` | Boundary |
| TC-011 | Boundary: score exactly 40 | Inputs producing exactly 40 | `priority = "medium"` | Boundary |
| TC-012 | Boundary: score exactly 39 | Inputs producing 39 | `priority = "low"` | Boundary |

### 5.2 Ingestion Tests

| Test ID | Description | Input | Expected Output | Type |
|---------|------------|-------|-----------------|------|
| TC-013 | Valid CSV ingestion | Well-formed CSV with all required fields | DataFrame with correct row count, `is_valid = True` | Functional |
| TC-014 | CSV with missing required columns | CSV without `email` column | `IngestionError` raised with message listing missing columns | Negative |
| TC-015 | Empty CSV | CSV with headers only, no data rows | `IngestionError` raised with "empty" message | Negative |
| TC-016 | CSV with missing field values | Row with empty `name` field | `ValidationResult.errors` contains row-specific error, row excluded from output | Negative |
| TC-017 | Duplicate emails in CSV | Two rows with same email | `ValidationResult.warnings` mentions duplicates, only first kept | Edge Case |
| TC-018 | Invalid email format | Row with email `"not-an-email"` | `ValidationResult.errors` contains email format error | Negative |
| TC-019 | Invalid date format | Row with date `"03/15/2025"` (wrong format) | `ValidationResult.errors` contains date format error | Negative |
| TC-020 | Invalid status value | Row with status `"unknown"` | `ValidationResult.errors` contains status error | Negative |
| TC-021 | Invalid company tier value | Row with tier `"mega"` | `ValidationResult.errors` contains tier error | Negative |

### 5.3 Analytics Tests

| Test ID | Description | Input | Expected Output | Type |
|---------|------------|-------|-----------------|------|
| TC-022 | Priority distribution | DataFrame with known priority values | Correct counts per priority level | Unit |
| TC-023 | Status breakdown | DataFrame with known status values | Correct counts per status | Unit |
| TC-024 | Contacts by company | DataFrame with known company values | Correct counts per company | Unit |
| TC-025 | Summary statistics | DataFrame with known data | Correct total, average, and priority counts | Unit |
| TC-026 | Empty DataFrame | Empty DataFrame with correct columns | Zero counts, zero average | Edge Case |

### 5.4 Export and Integration Tests

| Test ID | Description | Input | Expected Output | Type |
|---------|------------|-------|-----------------|------|
| TC-027 | CSV export | DataFrame with 5 contacts | Valid CSV bytes parseable back into same DataFrame | Functional |
| TC-028 | Database persistence | Insert contacts, restart session, query | All contacts retrieved with correct scores | Integration |
| TC-029 | End-to-end: upload to scored output | Upload CSV → score → store → retrieve | Contacts in DB with correct scores and priorities | Integration |

---

## 6. Test Data

### 6.1 Fixed Reference Date

All scoring tests use a fixed `reference_date = date(2025, 3, 26)` to ensure deterministic results regardless of when tests run.

### 6.2 Sample Test Contacts

```python
test_contacts = [
    {
        "name": "Test User A",
        "email": "a@test.com",
        "company": "TestCorp",
        "status": "lead",
        "company_tier": "enterprise",
        "last_contacted_date": "2024-12-15",  # 101 days → 30 + 25 + 30 = 85 (high)
    },
    {
        "name": "Test User B",
        "email": "b@test.com",
        "company": "TestCorp",
        "status": "active",
        "company_tier": "startup",
        "last_contacted_date": "2025-03-16",  # 10 days → 5 + 15 + 10 = 30 (low)
    },
    {
        "name": "Test User C",
        "email": "c@test.com",
        "company": "TestCorp",
        "status": "inactive",
        "company_tier": "mid-market",
        "last_contacted_date": "2025-02-09",  # 45 days → 10 + 20 + 20 = 50 (medium)
    },
]
```

---

## 7. Entry and Exit Criteria

### Entry Criteria

- All source code modules are implemented and syntactically valid
- Test fixtures and sample data are prepared
- pytest and pytest-cov are installed in the test environment

### Exit Criteria

- All test cases pass (zero failures)
- Line coverage meets or exceeds 80% threshold
- No critical or high-severity defects remain open
- CI pipeline runs green on both Python 3.11 and 3.12

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Scoring logic produces incorrect priorities at boundaries | Medium | High | Explicit boundary test cases (TC-009 through TC-012) |
| CSV with unexpected encoding causes parse failure | Low | Medium | Test with various CSV inputs; use pandas default encoding handling |
| Database file locked during concurrent access | Low | Low | SQLite with `check_same_thread=False`; single-user application |
| Date parsing fails for edge case formats | Medium | Medium | Strict YYYY-MM-DD validation; reject other formats with clear error |

---

## 9. Test Execution Schedule

| Phase | Tests | Timeline |
|-------|-------|---------|
| Unit Tests | TC-001 through TC-012, TC-022 through TC-026 | Sprint 1 |
| Functional Tests | TC-013 through TC-021, TC-027 | Sprint 1 |
| Integration Tests | TC-028, TC-029 | Sprint 2 |
| Regression | All | Every CI run |

---

## 10. Coverage Targets

| Module | Target Coverage | Rationale |
|--------|---------------|-----------|
| `app/scorer.py` | 95%+ | Critical business logic; all paths must be verified |
| `app/ingestion.py` | 90%+ | Data quality gate; validation logic must be thorough |
| `app/analytics.py` | 85%+ | Aggregation correctness is essential for dashboard accuracy |
| `app/exporter.py` | 80%+ | Simpler module; basic functionality coverage sufficient |
| `app/database.py` | 70%+ | ORM model definitions; less logic to test |
| **Overall** | **80%+** | **CI pipeline enforces this threshold** |
