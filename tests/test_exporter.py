import pandas as pd
from app.exporter import export_contacts_to_csv, export_filtered_contacts


class TestExportContactsToCSV:
    def test_returns_bytes(self):
        df = pd.DataFrame({"Name": ["Alice"], "Email": ["a@test.com"]})
        result = export_contacts_to_csv(df)
        assert isinstance(result, bytes)

    def test_contains_headers(self):
        df = pd.DataFrame({"Name": ["Alice"], "Email": ["a@test.com"]})
        result = export_contacts_to_csv(df).decode("utf-8")
        assert "Name" in result
        assert "Email" in result

    def test_contains_data_rows(self):
        df = pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Email": ["a@test.com", "b@test.com"],
        })
        result = export_contacts_to_csv(df).decode("utf-8")
        assert "Alice" in result
        assert "Bob" in result

    def test_empty_dataframe_returns_headers_only(self):
        df = pd.DataFrame(columns=["Name", "Email"])
        result = export_contacts_to_csv(df).decode("utf-8")
        assert "Name" in result
        lines = result.strip().split("\n")
        assert len(lines) == 1

    def test_preserves_all_columns(self):
        df = pd.DataFrame({
            "Name": ["Alice"],
            "Score": [85.0],
            "Priority": ["high"],
            "Company": ["TechCorp"],
        })
        result = export_contacts_to_csv(df).decode("utf-8")
        assert "Score" in result
        assert "Priority" in result
        assert "Company" in result
        assert "85.0" in result


class TestExportFilteredContacts:
    def test_returns_tuple_of_bytes_and_filename(self):
        df = pd.DataFrame({"Name": ["Alice"]})
        csv_bytes, filename = export_filtered_contacts(df)
        assert isinstance(csv_bytes, bytes)
        assert isinstance(filename, str)

    def test_default_filename(self):
        df = pd.DataFrame({"Name": ["Alice"]})
        _, filename = export_filtered_contacts(df)
        assert filename == "exported_contacts.csv"

    def test_custom_filename(self):
        df = pd.DataFrame({"Name": ["Alice"]})
        _, filename = export_filtered_contacts(df, filename="my_export.csv")
        assert filename == "my_export.csv"

    def test_csv_content_matches_dataframe(self):
        df = pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Email": ["a@test.com", "b@test.com"],
        })
        csv_bytes, _ = export_filtered_contacts(df)
        content = csv_bytes.decode("utf-8")
        assert "Alice" in content
        assert "Bob" in content
