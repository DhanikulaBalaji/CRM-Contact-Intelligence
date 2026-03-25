"""Analytics module providing aggregation functions for dashboard visualizations."""

import pandas as pd


def get_priority_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return df["Priority"].value_counts().reset_index()


def get_status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df["Status"].value_counts().reset_index()


def get_contacts_by_company(df: pd.DataFrame) -> pd.DataFrame:
    return df["Company"].value_counts().reset_index()


def get_score_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Score"]]


def get_summary_stats(df: pd.DataFrame) -> dict:
    return {
        "total_contacts": len(df),
        "avg_score": round(df["Score"].mean(), 1) if not df.empty else 0,
        "high_priority": len(df[df["Priority"] == "high"]),
        "medium_priority": len(df[df["Priority"] == "medium"]),
        "low_priority": len(df[df["Priority"] == "low"]),
    }
