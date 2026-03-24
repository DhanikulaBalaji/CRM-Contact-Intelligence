# CRM Contact Intelligence

![CI](https://github.com/DhanikulaBalaji/CRM-Contact-Intelligence/actions/workflows/ci.yml/badge.svg)

A data-driven platform that helps sales teams prioritize contacts through automated engagement scoring and visual analytics.

---

## Problem Statement

Sales teams managing hundreds or thousands of contacts face a common set of challenges:

- **Lost visibility**: Contacts are scattered across spreadsheets and tools with no unified engagement view.
- **No prioritization**: Without objective scoring, reps spend equal time on all contacts regardless of potential value.
- **Stale relationships**: Contacts that haven't been reached out to in months slip through the cracks.
- **Manual processes**: Re-processing contact data every session wastes valuable selling time.

CRM Contact Intelligence solves these problems by automating contact scoring and presenting results in an interactive, filterable dashboard.

---

## Solution Overview

Upload a CSV of your contacts, and the platform will:

1. **Validate** data for completeness and correctness
2. **Score** each contact (0–100) based on recency, status, and company tier
3. **Classify** contacts as high, medium, or low priority
4. **Persist** everything in a local SQLite database
5. **Visualize** results with interactive charts and filters
6. **Export** filtered contact lists as CSV for your CRM

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Presentation Layer (Streamlit)         │
│   Upload │ Filters │ Table │ Charts │ Export     │
└─────┬───────────┬──────────────┬────────────────┘
      │           │              │
      ▼           │              ▼
┌───────────┐     │     ┌──────────────┐
│ Ingestion │     │     │  Analytics   │
│  Layer    │     │     │   Layer      │
└─────┬─────┘     │     └──────┬───────┘
      │           │            │
      ▼           │            │
┌───────────┐     │            │
│  Scoring  │     │            │
│  Engine   │     │            │
└─────┬─────┘     │            │
      │           │            │
      ▼           ▼            ▼
┌─────────────────────────────────────────────────┐
│        Persistence Layer (SQLAlchemy + SQLite)   │
└─────────────────────────────────────────────────┘
```

---

## Scoring Algorithm

Each contact receives a score from 0 to 100 based on three weighted factors:

### Factor 1: Recency (Days Since Last Contact)

| Condition | Score |
|-----------|-------|
| > 90 days | 30 |
| 61–90 days | 20 |
| 31–60 days | 10 |
| ≤ 30 days | 5 |

### Factor 2: Contact Status

| Status | Score |
|--------|-------|
| Lead | 25 |
| Inactive | 20 |
| Active | 15 |
| Churned | 10 |

### Factor 3: Company Tier

| Tier | Score |
|------|-------|
| Enterprise | 30 |
| Mid-market | 20 |
| Startup | 10 |

### Priority Assignment

| Total Score | Priority |
|-------------|----------|
| > 70 | High |
| 40–70 | Medium |
| < 40 | Low |

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.11+ | Core language |
| Streamlit | Web UI framework |
| SQLite | Embedded database |
| SQLAlchemy | ORM |
| Pandas | Data manipulation |
| Plotly | Interactive charts |
| Pytest | Testing framework |

---

## Folder Structure

```
crm-contact-intelligence/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── app/
│   ├── __init__.py
│   ├── analytics.py            # Analytics aggregation functions
│   ├── database.py             # SQLAlchemy models and DB setup
│   ├── exporter.py             # CSV export utilities
│   ├── ingestion.py            # CSV parsing and validation
│   ├── main.py                 # Streamlit application entry point
│   └── scorer.py               # Scoring engine
├── data/
│   └── sample_contacts.csv     # 20 sample contact records
├── docs/
│   ├── design.md               # High-level design document
│   ├── lld.md                  # Low-level design document
│   ├── requirements.md         # Software requirements specification
│   └── test-plan.md            # Formal test plan
├── tests/
│   ├── __init__.py
│   ├── test_analytics.py       # Analytics module tests
│   ├── test_ingestion.py       # Ingestion module tests
│   └── test_scorer.py          # Scoring engine tests
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/DhanikulaBalaji/CRM-Contact-Intelligence.git
cd CRM-Contact-Intelligence

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app/main.py
```

The application will open in your browser at `http://localhost:8501`.

### Quick Start

1. Launch the app with the command above
2. Use the sidebar to upload `data/sample_contacts.csv` (or your own CSV)
3. View scored contacts in the dashboard table
4. Apply filters (status, company, priority) from the sidebar
5. Explore analytics charts below the table
6. Export filtered contacts using the download button

---

## Sample Data

The `data/sample_contacts.csv` file contains 20 realistic contact records spanning:

- **6 companies**: TechCorp, Innovate IO, StartupX, MegaCorp, CloudNine, DataFlow
- **4 statuses**: active, inactive, lead, churned
- **3 tiers**: enterprise, mid-market, startup
- **Date range**: May 2024 to March 2025

---

## Testing

### Run all tests

```bash
pytest -v
```

### Run tests with coverage report

```bash
pytest --cov=app --cov-report=term-missing -v
```

### Check coverage threshold (80%)

```bash
pytest --cov=app --cov-fail-under=80
```

### Run specific test files

```bash
pytest tests/test_scorer.py -v
pytest tests/test_ingestion.py -v
pytest tests/test_analytics.py -v
```

---

## License

This project is provided for educational and demonstration purposes.
