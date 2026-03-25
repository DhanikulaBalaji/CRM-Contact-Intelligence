"""Export utilities for converting contact DataFrames to downloadable CSV format."""

import io

import pandas as pd


def export_contacts_to_csv(contacts_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    contacts_df.to_csv(output, index=False)
    return output.getvalue()


def export_filtered_contacts(
    contacts_df: pd.DataFrame, filename: str = "exported_contacts.csv"
) -> tuple[bytes, str]:
    csv_bytes = export_contacts_to_csv(contacts_df)
    return csv_bytes, filename
