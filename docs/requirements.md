# Software Requirements Specification (SRS)

## CRM Contact Intelligence Platform

**Version:** 1.0
**Date:** 2025-03-24
**Author:** CRM Engineering Team

---

## 1. Introduction

### 1.1 Purpose

CRM Contact Intelligence is a data-driven platform designed to help sales teams prioritize their contacts through automated engagement scoring and visual analytics. The system ingests contact data from CSV files, applies a rules-based scoring algorithm, and presents actionable insights through an interactive dashboard.

### 1.2 Scope

The platform covers the full lifecycle of contact prioritization: data ingestion, validation, scoring, persistent storage, filtering, analytics visualization, and data export. It is built as a single-user desktop application powered by Streamlit with a SQLite backend.

### 1.3 Definitions and Acronyms

| Term | Definition |
|------|-----------|
| CRM | Customer Relationship Management |
| CSV | Comma-Separated Values |
| SRS | Software Requirements Specification |
| Engagement Score | A numeric value (0–100) representing how urgently a contact should be followed up |
| Priority | A categorical label (high, medium, low) derived from the engagement score |
| Company Tier | Classification of a company as enterprise, mid-market, or startup |

### 1.4 Intended Audience

- Sales managers seeking to optimize contact outreach
- Sales representatives who need clear prioritization guidance
- Development and QA teams building and testing the platform

---

## 2. Problem Statement

Sales teams face several critical challenges when managing large contact lists:

1. **Loss of Visibility**: Contacts are scattered across spreadsheets, email threads, and CRM tools with no unified view of engagement levels.
2. **No Engagement Tracking**: There is no systematic way to measure how recently or effectively contacts have been engaged, leading to stale relationships.
3. **Wasted Effort on Low-Priority Leads**: Without data-driven prioritization, sales reps spend equal time on all contacts regardless of their potential value or urgency.
4. **No Data-Driven Prioritization**: Decisions about who to call next are based on gut feeling rather than objective criteria such as recency of contact, account tier, and lead status.
5. **Manual and Error-Prone Processes**: Re-uploading and re-processing contact data every session is tedious and introduces the risk of data inconsistency.

CRM Contact Intelligence solves these problems by automating contact scoring based on configurable rules and presenting results in an intuitive, filterable dashboard with rich analytics.

---

## 3. Functional Requirements

| Req ID | Requirement | Description | Priority |
|--------|------------|-------------|----------|
| FR-001 | CSV Upload | The system shall allow users to upload contacts via a CSV file through the Streamlit sidebar. | High |
| FR-002 | CSV Validation | The system shall validate uploaded CSV data, checking for required fields (name, email, company, status, company_tier, last_contacted_date), correct formats (email, date), valid enum values (status, tier), and duplicate email addresses. | High |
| FR-003 | Engagement Scoring | The system shall calculate an engagement/priority score (0–100) for each contact based on days since last contact, contact status, and company tier. | High |
| FR-004 | Persistent Storage | The system shall store all contacts and their computed scores persistently in a SQLite database so that data survives application restarts. | High |
| FR-005 | Dashboard Table | The system shall display contacts in a sortable, filterable dashboard table showing all contact fields including computed score and priority. | High |
| FR-006 | Status Filter | The system shall allow users to filter contacts by status (active, inactive, lead, churned) via a sidebar dropdown. | Medium |
| FR-007 | Company Filter | The system shall allow users to filter contacts by company name via a sidebar dropdown. | Medium |
| FR-008 | Priority Filter | The system shall allow users to filter contacts by priority level (high, medium, low) via a sidebar dropdown. | Medium |
| FR-009 | Analytics Charts | The system shall display interactive analytics charts including priority distribution (pie), status breakdown (bar), contacts by company (bar), and score distribution (histogram). | Medium |
| FR-010 | CSV Export | The system shall allow users to export the currently filtered contact list to a downloadable CSV file. | Medium |
| FR-011 | Score Breakdown | The system shall provide a detailed score breakdown for each contact showing individual component scores (days score, status score, tier score) and total. | Low |
| FR-012 | Session Persistence | The system shall persist all scoring results across sessions so that users do not need to re-upload or re-score contacts every time the application is launched. | High |

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **NFR-001**: The scoring engine shall process and score 1,000 contacts in under 5 seconds on commodity hardware.
- **NFR-002**: The dashboard shall render the contact table and all analytics charts within 3 seconds of page load for datasets up to 5,000 contacts.
- **NFR-003**: CSV ingestion and validation shall complete within 2 seconds for files containing up to 1,000 rows.

### 4.2 Data Integrity

- **NFR-004**: The system shall enforce unique email constraints at the database level to prevent duplicate contacts.
- **NFR-005**: The system shall perform upsert operations (update if email exists, insert if new) during CSV import to maintain data consistency.
- **NFR-006**: All validation errors shall be reported to the user with specific row numbers and field names.

### 4.3 Usability

- **NFR-007**: The application shall provide an intuitive Streamlit-based UI that requires no training for basic operations (upload, filter, view).
- **NFR-008**: All interactive elements (filters, upload, export) shall be accessible from the sidebar for a clean layout.
- **NFR-009**: Error messages shall be clear, actionable, and displayed prominently in the UI.

### 4.4 Maintainability

- **NFR-010**: The codebase shall maintain at least 80% test coverage as measured by pytest-cov.
- **NFR-011**: The system shall follow a modular architecture with clear separation of concerns (ingestion, scoring, persistence, analytics, presentation).

### 4.5 Portability

- **NFR-012**: The system shall run on Python 3.11+ with no platform-specific dependencies.
- **NFR-013**: SQLite shall be used as the database to ensure zero-configuration deployment.

---

## 5. User Stories

### US-001: Upload Contact List

**As a** sales manager,
**I want to** upload my contact list via a CSV file,
**So that** I can analyze engagement levels across all my contacts in one place.

### US-002: Automatic Contact Scoring

**As a** sales manager,
**I want** contacts to be scored automatically upon upload,
**So that** I immediately know who to call first based on objective criteria.

### US-003: Filter by Status

**As a** sales manager,
**I want to** filter contacts by their status (active, inactive, lead, churned),
**So that** I can focus on specific segments of my pipeline.

### US-004: Visual Analytics

**As a** sales manager,
**I want to** see analytics charts showing priority distribution, status breakdown, and company distribution,
**So that** I can get quick visual insights into my contact portfolio.

### US-005: Export Filtered Contacts

**As a** sales manager,
**I want to** export the currently filtered contact list as a CSV file,
**So that** I can share the data with my team or import it into other CRM tools.

### US-006: Data Persistence

**As a** sales manager,
**I want** my contact data and scores to be persisted across sessions,
**So that** I don't have to re-upload and re-process my contact list every time I open the application.

### US-007: Sort by Score

**As a** sales manager,
**I want to** sort contacts by their engagement score in descending order,
**So that** I can quickly identify the highest-priority contacts that need immediate attention.

### US-008: Score Breakdown

**As a** sales manager,
**I want to** see a detailed breakdown of how each contact's score was calculated,
**So that** I understand the reasoning behind the prioritization and can trust the system's recommendations.

---

## 6. Acceptance Criteria

### AC for US-001: Upload Contact List

- [ ] User can upload a CSV file via the sidebar file uploader
- [ ] System accepts files with .csv extension only
- [ ] Upon successful upload, contacts appear in the dashboard table
- [ ] Upload errors are displayed clearly in the sidebar
- [ ] Previously uploaded contacts are preserved (upsert behavior)

### AC for US-002: Automatic Contact Scoring

- [ ] Each contact receives a score between 0 and 100
- [ ] Each contact is assigned a priority label: high (>70), medium (40–70), or low (<40)
- [ ] Scores are computed based on days since last contact, status weight, and company tier weight
- [ ] Scores are calculated immediately upon CSV upload without manual trigger
- [ ] Scored contacts are persisted to the database

### AC for US-003: Filter by Status

- [ ] A "Status" dropdown appears in the sidebar with options: All, active, inactive, lead, churned
- [ ] Selecting a status filters the dashboard table to show only matching contacts
- [ ] The "All" option shows contacts of every status
- [ ] Filter is applied immediately upon selection
- [ ] Contact count updates to reflect filtered results

### AC for US-004: Visual Analytics

- [ ] A priority distribution pie chart is displayed below the contact table
- [ ] A status breakdown bar chart is displayed
- [ ] A contacts-by-company bar chart is displayed
- [ ] A score distribution histogram is displayed
- [ ] All charts use Plotly for interactivity (hover, zoom)
- [ ] Charts update when filters are applied

### AC for US-005: Export Filtered Contacts

- [ ] An "Export" button is visible below the contact table
- [ ] Clicking the button downloads a CSV file containing only the currently filtered contacts
- [ ] The exported CSV includes all displayed columns
- [ ] The downloaded file has a descriptive filename (e.g., filtered_contacts.csv)

### AC for US-006: Data Persistence

- [ ] Contacts uploaded in one session are available when the application is restarted
- [ ] Scores and priority labels persist across sessions
- [ ] The SQLite database file is created in the project directory
- [ ] No data loss occurs during normal application shutdown

### AC for US-007: Sort by Score

- [ ] The contact table is sorted by score in descending order by default
- [ ] Users can click column headers to re-sort by other fields
- [ ] Sort order is visually indicated in the table header

### AC for US-008: Score Breakdown

- [ ] A score breakdown function returns individual component scores
- [ ] The breakdown includes: days_since_contact, days_score, status_score, tier_score, total_score, priority
- [ ] Component scores sum to the total score (capped at 100)
- [ ] The breakdown is accessible programmatically for each contact
