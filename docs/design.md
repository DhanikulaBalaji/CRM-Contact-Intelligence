# High-Level Design (HLD)

## CRM Contact Intelligence Platform

**Version:** 1.0
**Date:** 2025-03-24
**Author:** CRM Engineering Team

---

## 1. System Architecture

The CRM Contact Intelligence platform follows a layered architecture with five distinct layers, each responsible for a specific concern. This separation ensures modularity, testability, and ease of maintenance.

### 1.1 Data Ingestion Layer (`app/ingestion.py`)

Responsible for reading CSV files, parsing contact records, and validating data integrity. This layer enforces schema constraints (required fields, data types, valid enumerations) and handles deduplication. It produces a clean Pandas DataFrame ready for downstream processing.

### 1.2 Scoring Engine (`app/scorer.py`)

Implements the rules-based engagement scoring algorithm. Takes validated contact records and computes a numerical score (0–100) based on three weighted factors: recency of last contact, contact status, and company tier. Assigns a priority label (high, medium, low) based on score thresholds.

### 1.3 Persistence Layer (`app/database.py`)

Manages all database operations using SQLAlchemy ORM backed by SQLite. Provides the Contact data model, session management, upsert logic, and query interfaces. Ensures data survives application restarts with zero configuration.

### 1.4 Analytics Layer (`app/analytics.py`)

Transforms stored contact data into aggregated metrics and distributions suitable for visualization. Computes summary statistics, priority distributions, status breakdowns, company distributions, and score histograms.

### 1.5 Presentation Layer (`app/main.py`)

The Streamlit-based user interface that ties all layers together. Provides the CSV upload widget, filter controls, contact data table, analytics charts (via Plotly), and CSV export functionality. Acts as the orchestrator calling into other layers.

---

## 2. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│                      (Streamlit - app/main.py)                      │
│                                                                     │
│   ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐  │
│   │  Upload   │  │  Dashboard   │  │  Filters │  │   Export      │  │
│   │  Widget   │  │  Table       │  │  Sidebar │  │   Button      │  │
│   └────┬─────┘  └──────▲───────┘  └────┬─────┘  └──────▲───────┘  │
│        │               │               │               │           │
└────────┼───────────────┼───────────────┼───────────────┼───────────┘
         │               │               │               │
         ▼               │               ▼               │
┌─────────────────┐      │      ┌─────────────────┐      │
│   INGESTION     │      │      │   ANALYTICS     │      │
│   LAYER         │      │      │   LAYER         │      │
│                 │      │      │                 │      │
│  ┌───────────┐  │      │      │  ┌───────────┐  │      │
│  │ CSV Parse │  │      │      │  │ Priority  │  │      │
│  │ Validate  │  │      │      │  │ Status    │  │      │
│  │ Dedup     │  │      │      │  │ Company   │  │      │
│  └─────┬─────┘  │      │      │  │ Score     │  │      │
│        │        │      │      │  └─────┬─────┘  │      │
└────────┼────────┘      │      └────────┼────────┘      │
         │               │               │               │
         ▼               │               ▼               │
┌─────────────────┐      │      ┌─────────────────────────┐
│  SCORING        │      │      │      EXPORTER           │
│  ENGINE         │      │      │  (app/exporter.py)      │
│                 │      │      │                         │
│  ┌───────────┐  │      │      │  ┌───────────────────┐  │
│  │ Days Score│  │      │      │  │ DataFrame → CSV   │  │
│  │ Status    │  │      │      │  │ Download Button   │  │
│  │ Tier      │  │      │      │  └───────────────────┘  │
│  │ Priority  │  │      │      └─────────────────────────┘
│  └─────┬─────┘  │      │
│        │        │      │
└────────┼────────┘      │
         │               │
         ▼               │
┌─────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                      │
│               (SQLAlchemy + SQLite)                       │
│                                                          │
│   ┌──────────────────────────────────────────────────┐   │
│   │              contacts TABLE                       │   │
│   │                                                   │   │
│   │  id | name | email | phone | company | status |   │   │
│   │  company_tier | last_contacted_date | notes |     │   │
│   │  score | priority                                 │   │
│   └──────────────────────────────────────────────────┘   │
│                                                          │
│   Indexes: email (unique), status, company, priority     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram

### 3.1 CSV Upload to Dashboard Display

```
Step 1: User uploads CSV file via Streamlit sidebar
            │
            ▼
Step 2: Ingestion Layer reads and parses CSV
            │
            ├── Validates required columns exist
            ├── Validates each row (email format, date format, enums)
            ├── Reports validation errors/warnings
            └── Removes duplicate emails (keeps first occurrence)
            │
            ▼
Step 3: Scoring Engine processes validated contacts
            │
            ├── Calculates days since last contact
            ├── Looks up status weight
            ├── Looks up company tier weight
            ├── Sums component scores (capped at 100)
            └── Assigns priority label based on thresholds
            │
            ▼
Step 4: Persistence Layer stores scored contacts
            │
            ├── Checks if email already exists in database
            ├── Updates existing records (upsert)
            ├── Inserts new records
            └── Commits transaction
            │
            ▼
Step 5: Presentation Layer loads contacts from database
            │
            ├── Converts to Pandas DataFrame
            ├── Applies user-selected filters
            ├── Renders sortable data table
            └── Displays analytics charts
            │
            ▼
Step 6: User interacts with dashboard
            │
            ├── Filters by status, company, priority
            ├── Sorts by any column
            ├── Views analytics visualizations
            └── Exports filtered data to CSV
```

### 3.2 Filter and Export Flow

```
User selects filter → DataFrame filtered in-memory → Table re-rendered
                                                    → Charts re-rendered
                                                    → Export button updated with filtered data
```

---

## 4. Tech Stack Justification

| Technology | Role | Justification |
|-----------|------|---------------|
| **Python 3.11+** | Core Language | Rich data science ecosystem, excellent library support for data manipulation and web UIs, widely adopted in analytics tooling |
| **Streamlit 1.38** | Web UI Framework | Enables rapid development of data-centric web applications with minimal boilerplate; built-in widgets for file upload, tables, and interactive charts; hot-reload during development |
| **SQLite** | Database | Zero-configuration embedded database; no server process needed; single-file storage simplifies deployment; sufficient performance for single-user workloads up to tens of thousands of records |
| **SQLAlchemy 2.0** | ORM | Industry-standard Python ORM; provides type-safe model definitions, migration support, and query building; abstracts database operations from business logic |
| **Pandas 2.2** | Data Manipulation | De facto standard for tabular data processing in Python; efficient CSV parsing, filtering, grouping, and transformation; seamless integration with Streamlit and Plotly |
| **Plotly 5.24** | Visualization | Interactive charts with hover tooltips, zoom, and export; wide range of chart types (pie, bar, histogram); first-class Streamlit integration via `st.plotly_chart` |
| **Pytest 8.3** | Testing Framework | Simple and powerful test framework; excellent fixture system; rich plugin ecosystem including coverage reporting via pytest-cov |
| **pytest-cov 5.0** | Coverage Reporting | Integrates seamlessly with pytest; provides terminal and XML coverage reports; supports minimum coverage threshold enforcement in CI |

---

## 5. Interface Contracts

### 5.1 Ingestion Module (`app/ingestion.py`)

```python
def ingest_csv(file_path_or_buffer) -> tuple[pd.DataFrame, ValidationResult]:
    """
    Parse and validate a CSV file or buffer.
    
    Args:
        file_path_or_buffer: File path string or file-like object (e.g., Streamlit UploadedFile)
    
    Returns:
        tuple of (valid_dataframe, validation_result)
    
    Raises:
        IngestionError: If the file cannot be read, is empty, or is missing required columns
    """
```

### 5.2 Scoring Module (`app/scorer.py`)

```python
def calculate_score(
    last_contacted_date: date,
    status: str,
    company_tier: str,
    reference_date: Optional[date] = None,
) -> tuple[float, str]:
    """
    Calculate engagement score and priority for a single contact.
    
    Returns:
        tuple of (score: float 0-100, priority: str "high"/"medium"/"low")
    """

def score_contacts(
    contacts: list[dict],
    reference_date: Optional[date] = None,
) -> list[dict]:
    """
    Score a list of contact dictionaries in bulk.
    
    Returns:
        New list of dicts with 'score' and 'priority' fields added.
    """

def get_score_breakdown(
    last_contacted_date: date,
    status: str,
    company_tier: str,
    reference_date: Optional[date] = None,
) -> dict:
    """
    Return detailed scoring breakdown for a single contact.
    
    Returns:
        dict with keys: days_since_contact, days_score, status_score,
        tier_score, total_score, priority
    """
```

### 5.3 Database Module (`app/database.py`)

```python
def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session, closing it after use."""

def init_db() -> None:
    """Create all tables if they do not exist."""
```

### 5.4 Analytics Module (`app/analytics.py`)

```python
def get_priority_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return priority value counts as a DataFrame."""

def get_status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return status value counts as a DataFrame."""

def get_contacts_by_company(df: pd.DataFrame) -> pd.DataFrame:
    """Return contact counts grouped by company."""

def get_summary_stats(df: pd.DataFrame) -> dict:
    """Return summary statistics dict with total, averages, and priority counts."""
```

### 5.5 Exporter Module (`app/exporter.py`)

```python
def export_contacts_to_csv(contacts_df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for download."""

def export_filtered_contacts(
    contacts_df: pd.DataFrame,
    filename: str = "exported_contacts.csv",
) -> tuple[bytes, str]:
    """Export filtered contacts, returning (csv_bytes, filename)."""
```
