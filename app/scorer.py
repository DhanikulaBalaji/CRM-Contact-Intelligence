"""Rules-based contact scoring engine computing engagement priority from recency, status, and tier."""

from datetime import date, datetime
from typing import Optional


STATUS_WEIGHTS = {
    "lead": 25,
    "inactive": 20,
    "active": 15,
    "churned": 10,
}

TIER_WEIGHTS = {
    "enterprise": 30,
    "mid-market": 20,
    "startup": 10,
}


def calculate_days_score(days_since_contact: int) -> int:
    if days_since_contact > 90:
        return 30
    elif days_since_contact > 60:
        return 20
    elif days_since_contact > 30:
        return 10
    else:
        return 5


def calculate_status_score(status: str) -> int:
    return STATUS_WEIGHTS.get(status.lower(), 0)


def calculate_tier_score(company_tier: str) -> int:
    return TIER_WEIGHTS.get(company_tier.lower(), 0)


def calculate_score(
    last_contacted_date: date,
    status: str,
    company_tier: str,
    reference_date: Optional[date] = None,
) -> tuple[float, str]:
    if reference_date is None:
        reference_date = date.today()

    days_since = (reference_date - last_contacted_date).days

    days_score = calculate_days_score(days_since)
    status_score = calculate_status_score(status)
    tier_score = calculate_tier_score(company_tier)

    total_score = min(days_score + status_score + tier_score, 100)

    if total_score > 70:
        priority = "high"
    elif total_score >= 40:
        priority = "medium"
    else:
        priority = "low"

    return float(total_score), priority


def get_score_breakdown(
    last_contacted_date: date,
    status: str,
    company_tier: str,
    reference_date: Optional[date] = None,
) -> dict:
    if reference_date is None:
        reference_date = date.today()
    days_since = (reference_date - last_contacted_date).days
    days_score = calculate_days_score(days_since)
    status_score = calculate_status_score(status)
    tier_score = calculate_tier_score(company_tier)
    total = min(days_score + status_score + tier_score, 100)
    priority = "high" if total > 70 else "medium" if total >= 40 else "low"
    return {
        "days_since_contact": days_since,
        "days_score": days_score,
        "status_score": status_score,
        "tier_score": tier_score,
        "total_score": total,
        "priority": priority,
    }


def score_contacts(contacts: list[dict], reference_date: Optional[date] = None) -> list[dict]:
    scored = []
    for contact in contacts:
        last_date = contact["last_contacted_date"]
        if isinstance(last_date, str):
            last_date = datetime.strptime(last_date, "%Y-%m-%d").date()

        score, priority = calculate_score(
            last_contacted_date=last_date,
            status=contact["status"],
            company_tier=contact["company_tier"],
            reference_date=reference_date,
        )
        contact_copy = contact.copy()
        contact_copy["score"] = score
        contact_copy["priority"] = priority
        scored.append(contact_copy)

    return scored
