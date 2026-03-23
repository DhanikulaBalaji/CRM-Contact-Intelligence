import pytest
import pandas as pd
from app.analytics import (
    get_priority_distribution,
    get_status_breakdown,
    get_contacts_by_company,
    get_score_distribution,
    get_summary_stats,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Carol", "David", "Eva"],
        "Email": ["a@t.com", "b@t.com", "c@t.com", "d@t.com", "e@t.com"],
        "Company": ["TechCorp", "TechCorp", "StartupX", "TechCorp", "StartupX"],
        "Status": ["active", "lead", "active", "inactive", "lead"],
        "Priority": ["high", "high", "medium", "low", "medium"],
        "Score": [85.0, 75.0, 50.0, 30.0, 45.0],
    })


@pytest.fixture
def empty_df():
    return pd.DataFrame({
        "Name": pd.Series(dtype="str"),
        "Email": pd.Series(dtype="str"),
        "Company": pd.Series(dtype="str"),
        "Status": pd.Series(dtype="str"),
        "Priority": pd.Series(dtype="str"),
        "Score": pd.Series(dtype="float"),
    })


@pytest.fixture
def single_row_df():
    return pd.DataFrame({
        "Name": ["Alice"],
        "Email": ["a@t.com"],
        "Company": ["TechCorp"],
        "Status": ["active"],
        "Priority": ["high"],
        "Score": [85.0],
    })


class TestGetPriorityDistribution:
    def test_returns_correct_counts(self, sample_df):
        result = get_priority_distribution(sample_df)
        assert len(result) == 3
        high_count = result[result["Priority"] == "high"]["count"].values[0]
        medium_count = result[result["Priority"] == "medium"]["count"].values[0]
        low_count = result[result["Priority"] == "low"]["count"].values[0]
        assert high_count == 2
        assert medium_count == 2
        assert low_count == 1

    def test_empty_dataframe(self, empty_df):
        result = get_priority_distribution(empty_df)
        assert len(result) == 0

    def test_single_row(self, single_row_df):
        result = get_priority_distribution(single_row_df)
        assert len(result) == 1


class TestGetStatusBreakdown:
    def test_returns_correct_counts(self, sample_df):
        result = get_status_breakdown(sample_df)
        assert len(result) == 3
        active_count = result[result["Status"] == "active"]["count"].values[0]
        lead_count = result[result["Status"] == "lead"]["count"].values[0]
        inactive_count = result[result["Status"] == "inactive"]["count"].values[0]
        assert active_count == 2
        assert lead_count == 2
        assert inactive_count == 1

    def test_empty_dataframe(self, empty_df):
        result = get_status_breakdown(empty_df)
        assert len(result) == 0

    def test_single_row(self, single_row_df):
        result = get_status_breakdown(single_row_df)
        assert len(result) == 1


class TestGetContactsByCompany:
    def test_returns_correct_counts(self, sample_df):
        result = get_contacts_by_company(sample_df)
        assert len(result) == 2
        techcorp_count = result[result["Company"] == "TechCorp"]["count"].values[0]
        startupx_count = result[result["Company"] == "StartupX"]["count"].values[0]
        assert techcorp_count == 3
        assert startupx_count == 2

    def test_empty_dataframe(self, empty_df):
        result = get_contacts_by_company(empty_df)
        assert len(result) == 0


class TestGetScoreDistribution:
    def test_returns_score_column(self, sample_df):
        result = get_score_distribution(sample_df)
        assert "Score" in result.columns
        assert len(result) == 5

    def test_empty_dataframe(self, empty_df):
        result = get_score_distribution(empty_df)
        assert len(result) == 0


class TestGetSummaryStats:
    def test_correct_stats(self, sample_df):
        stats = get_summary_stats(sample_df)
        assert stats["total_contacts"] == 5
        assert stats["avg_score"] == 57.0
        assert stats["high_priority"] == 2
        assert stats["medium_priority"] == 2
        assert stats["low_priority"] == 1

    def test_empty_dataframe(self, empty_df):
        stats = get_summary_stats(empty_df)
        assert stats["total_contacts"] == 0
        assert stats["avg_score"] == 0
        assert stats["high_priority"] == 0
        assert stats["medium_priority"] == 0
        assert stats["low_priority"] == 0

    def test_single_row(self, single_row_df):
        stats = get_summary_stats(single_row_df)
        assert stats["total_contacts"] == 1
        assert stats["avg_score"] == 85.0
        assert stats["high_priority"] == 1
        assert stats["medium_priority"] == 0
        assert stats["low_priority"] == 0
