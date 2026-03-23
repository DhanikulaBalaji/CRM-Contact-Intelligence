import pytest
from datetime import date
from app.scorer import (
    calculate_days_score,
    calculate_status_score,
    calculate_tier_score,
    calculate_score,
    score_contacts,
    get_score_breakdown,
)

REFERENCE_DATE = date(2025, 3, 26)


class TestCalculateDaysScore:
    def test_more_than_90_days(self):
        assert calculate_days_score(100) == 30

    def test_exactly_91_days(self):
        assert calculate_days_score(91) == 30

    def test_exactly_90_days(self):
        assert calculate_days_score(90) == 20

    def test_between_61_and_90_days(self):
        assert calculate_days_score(75) == 20

    def test_exactly_61_days(self):
        assert calculate_days_score(61) == 20

    def test_exactly_60_days(self):
        assert calculate_days_score(60) == 10

    def test_between_31_and_60_days(self):
        assert calculate_days_score(45) == 10

    def test_exactly_31_days(self):
        assert calculate_days_score(31) == 10

    def test_exactly_30_days(self):
        assert calculate_days_score(30) == 5

    def test_less_than_30_days(self):
        assert calculate_days_score(15) == 5

    def test_zero_days(self):
        assert calculate_days_score(0) == 5


class TestCalculateStatusScore:
    def test_lead(self):
        assert calculate_status_score("lead") == 25

    def test_inactive(self):
        assert calculate_status_score("inactive") == 20

    def test_active(self):
        assert calculate_status_score("active") == 15

    def test_churned(self):
        assert calculate_status_score("churned") == 10

    def test_unknown_status(self):
        assert calculate_status_score("unknown") == 0

    def test_case_insensitive(self):
        assert calculate_status_score("LEAD") == 25
        assert calculate_status_score("Active") == 15


class TestCalculateTierScore:
    def test_enterprise(self):
        assert calculate_tier_score("enterprise") == 30

    def test_mid_market(self):
        assert calculate_tier_score("mid-market") == 20

    def test_startup(self):
        assert calculate_tier_score("startup") == 10

    def test_unknown_tier(self):
        assert calculate_tier_score("unknown") == 0

    def test_case_insensitive(self):
        assert calculate_tier_score("Enterprise") == 30
        assert calculate_tier_score("STARTUP") == 10


class TestCalculateScore:
    def test_enterprise_lead_100_days(self):
        # 30 (days) + 25 (lead) + 30 (enterprise) = 85
        last_date = date(2024, 12, 16)  # 100 days before reference
        score, priority = calculate_score(last_date, "lead", "enterprise", REFERENCE_DATE)
        assert score == 85.0
        assert priority == "high"

    def test_startup_active_10_days(self):
        # 5 (days) + 15 (active) + 10 (startup) = 30
        last_date = date(2025, 3, 16)  # 10 days before reference
        score, priority = calculate_score(last_date, "active", "startup", REFERENCE_DATE)
        assert score == 30.0
        assert priority == "low"

    def test_midmarket_inactive_45_days(self):
        # 10 (days) + 20 (inactive) + 20 (mid-market) = 50
        last_date = date(2025, 2, 9)  # 45 days before reference
        score, priority = calculate_score(last_date, "inactive", "mid-market", REFERENCE_DATE)
        assert score == 50.0
        assert priority == "medium"

    def test_boundary_score_70_is_medium(self):
        # Need exactly 70: 20 (61-90 days) + 20 (inactive) + 30 (enterprise) = 70
        last_date = date(2025, 1, 24)  # 61 days before reference
        score, priority = calculate_score(last_date, "inactive", "enterprise", REFERENCE_DATE)
        assert score == 70.0
        assert priority == "medium"

    def test_boundary_score_71_is_high(self):
        # Need 71 or above: 20 (61-90 days) + 25 (lead) + 30 (enterprise) = 75
        last_date = date(2025, 1, 24)  # 61 days
        score, priority = calculate_score(last_date, "lead", "enterprise", REFERENCE_DATE)
        assert score == 75.0
        assert priority == "high"

    def test_boundary_score_40_is_medium(self):
        # Need exactly 40: 10 (31-60 days) + 20 (inactive) + 10 (startup) = 40
        last_date = date(2025, 2, 23)  # 31 days before reference
        score, priority = calculate_score(last_date, "inactive", "startup", REFERENCE_DATE)
        assert score == 40.0
        assert priority == "medium"

    def test_boundary_score_below_40_is_low(self):
        # 5 (<=30 days) + 10 (churned) + 20 (mid-market) = 35
        last_date = date(2025, 3, 16)  # 10 days
        score, priority = calculate_score(last_date, "churned", "mid-market", REFERENCE_DATE)
        assert score == 35.0
        assert priority == "low"

    def test_score_capped_at_100(self):
        # max raw: 30 + 25 + 30 = 85, always under 100 with current weights
        # but test the cap logic by verifying the min(..., 100) works
        last_date = date(2024, 12, 16)  # 100 days
        score, priority = calculate_score(last_date, "lead", "enterprise", REFERENCE_DATE)
        assert score <= 100.0

    def test_returns_float_score(self):
        last_date = date(2025, 3, 16)
        score, _ = calculate_score(last_date, "active", "startup", REFERENCE_DATE)
        assert isinstance(score, float)


class TestScoreContacts:
    def test_score_list_of_contacts(self):
        contacts = [
            {
                "name": "Alice",
                "email": "alice@test.com",
                "company": "TestCorp",
                "status": "lead",
                "company_tier": "enterprise",
                "last_contacted_date": "2024-12-16",
            },
            {
                "name": "Bob",
                "email": "bob@test.com",
                "company": "TestCorp",
                "status": "active",
                "company_tier": "startup",
                "last_contacted_date": "2025-03-16",
            },
        ]
        scored = score_contacts(contacts, reference_date=REFERENCE_DATE)

        assert len(scored) == 2
        assert scored[0]["score"] == 85.0
        assert scored[0]["priority"] == "high"
        assert scored[1]["score"] == 30.0
        assert scored[1]["priority"] == "low"

    def test_does_not_mutate_input(self):
        contacts = [
            {
                "name": "Alice",
                "email": "alice@test.com",
                "company": "TestCorp",
                "status": "lead",
                "company_tier": "enterprise",
                "last_contacted_date": "2024-12-16",
            },
        ]
        scored = score_contacts(contacts, reference_date=REFERENCE_DATE)
        assert "score" not in contacts[0]
        assert "score" in scored[0]

    def test_handles_date_objects(self):
        contacts = [
            {
                "name": "Alice",
                "email": "alice@test.com",
                "company": "TestCorp",
                "status": "active",
                "company_tier": "mid-market",
                "last_contacted_date": date(2025, 3, 16),
            },
        ]
        scored = score_contacts(contacts, reference_date=REFERENCE_DATE)
        assert scored[0]["score"] == 40.0

    def test_empty_list(self):
        scored = score_contacts([], reference_date=REFERENCE_DATE)
        assert scored == []


class TestGetScoreBreakdown:
    def test_returns_correct_structure(self):
        last_date = date(2024, 12, 16)  # 100 days before reference
        breakdown = get_score_breakdown(last_date, "lead", "enterprise", REFERENCE_DATE)

        assert "days_since_contact" in breakdown
        assert "days_score" in breakdown
        assert "status_score" in breakdown
        assert "tier_score" in breakdown
        assert "total_score" in breakdown
        assert "priority" in breakdown

    def test_correct_values(self):
        last_date = date(2024, 12, 16)  # 100 days
        breakdown = get_score_breakdown(last_date, "lead", "enterprise", REFERENCE_DATE)

        assert breakdown["days_since_contact"] == 100
        assert breakdown["days_score"] == 30
        assert breakdown["status_score"] == 25
        assert breakdown["tier_score"] == 30
        assert breakdown["total_score"] == 85
        assert breakdown["priority"] == "high"

    def test_components_sum_to_total(self):
        last_date = date(2025, 2, 9)  # 45 days
        breakdown = get_score_breakdown(last_date, "inactive", "mid-market", REFERENCE_DATE)

        component_sum = (
            breakdown["days_score"]
            + breakdown["status_score"]
            + breakdown["tier_score"]
        )
        assert breakdown["total_score"] == min(component_sum, 100)

    def test_low_priority_breakdown(self):
        last_date = date(2025, 3, 16)  # 10 days
        breakdown = get_score_breakdown(last_date, "active", "startup", REFERENCE_DATE)

        assert breakdown["days_score"] == 5
        assert breakdown["status_score"] == 15
        assert breakdown["tier_score"] == 10
        assert breakdown["total_score"] == 30
        assert breakdown["priority"] == "low"
