import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from app.database import init_db, SessionLocal, Contact
from app.ingestion import ingest_csv, IngestionError
from app.scorer import score_contacts
from app.analytics import (
    get_priority_distribution,
    get_status_breakdown,
    get_contacts_by_company,
    get_score_distribution,
    get_summary_stats,
)

init_db()

st.set_page_config(page_title="CRM Contact Intelligence", layout="wide")
st.title("CRM Contact Intelligence Platform")

# Sidebar
st.sidebar.header("Controls")

uploaded_file = st.sidebar.file_uploader("Upload Contacts CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df, validation = ingest_csv(uploaded_file)

        if validation.errors:
            st.sidebar.warning(f"{validation.invalid_rows} invalid rows found")
            with st.sidebar.expander("Validation Errors"):
                for err in validation.errors:
                    st.write(f"- {err}")

        if validation.warnings:
            for warn in validation.warnings:
                st.sidebar.info(warn)

        if not df.empty:
            contacts = df.to_dict("records")
            scored = score_contacts(contacts)

            db = SessionLocal()
            try:
                for c in scored:
                    existing = db.query(Contact).filter(Contact.email == c["email"]).first()
                    if existing:
                        existing.name = c["name"]
                        existing.phone = c.get("phone", "")
                        existing.company = c["company"]
                        existing.status = c["status"]
                        existing.company_tier = c["company_tier"]
                        existing.last_contacted_date = datetime.strptime(
                            str(c["last_contacted_date"]), "%Y-%m-%d"
                        ).date()
                        existing.notes = c.get("notes", "")
                        existing.score = c["score"]
                        existing.priority = c["priority"]
                    else:
                        db_contact = Contact(
                            name=c["name"],
                            email=c["email"],
                            phone=c.get("phone", ""),
                            company=c["company"],
                            status=c["status"],
                            company_tier=c["company_tier"],
                            last_contacted_date=datetime.strptime(
                                str(c["last_contacted_date"]), "%Y-%m-%d"
                            ).date(),
                            notes=c.get("notes", ""),
                            score=c["score"],
                            priority=c["priority"],
                        )
                        db.add(db_contact)
                db.commit()
                st.sidebar.success(f"Imported {len(scored)} contacts successfully!")
            finally:
                db.close()
    except IngestionError as e:
        st.sidebar.error(str(e))

# Load contacts from database
db = SessionLocal()
contacts = db.query(Contact).all()
db.close()

if not contacts:
    st.info("No contacts yet. Upload a CSV file from the sidebar to get started.")
    st.stop()

df = pd.DataFrame([{
    "ID": c.id,
    "Name": c.name,
    "Email": c.email,
    "Phone": c.phone,
    "Company": c.company,
    "Status": c.status,
    "Tier": c.company_tier,
    "Last Contacted": str(c.last_contacted_date),
    "Score": c.score,
    "Priority": c.priority,
    "Notes": c.notes,
} for c in contacts])

# Sidebar filters
st.sidebar.header("Filters")
statuses = ["All"] + sorted(df["Status"].unique().tolist())
selected_status = st.sidebar.selectbox("Status", statuses)

companies = ["All"] + sorted(df["Company"].unique().tolist())
selected_company = st.sidebar.selectbox("Company", companies)

priorities = ["All"] + sorted(df["Priority"].unique().tolist())
selected_priority = st.sidebar.selectbox("Priority", priorities)

filtered_df = df.copy()
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_company != "All":
    filtered_df = filtered_df[filtered_df["Company"] == selected_company]
if selected_priority != "All":
    filtered_df = filtered_df[filtered_df["Priority"] == selected_priority]

st.subheader(f"Contacts ({len(filtered_df)} shown)")
st.dataframe(
    filtered_df.sort_values("Score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

# Export
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Export Filtered Contacts as CSV",
    data=csv_data,
    file_name="filtered_contacts.csv",
    mime="text/csv",
)

# Analytics
st.markdown("---")
st.subheader("Analytics Dashboard")

stats = get_summary_stats(filtered_df)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Contacts", stats["total_contacts"])
col2.metric("Avg Score", stats["avg_score"])
col3.metric("High Priority", stats["high_priority"])
col4.metric("Medium Priority", stats["medium_priority"])
col5.metric("Low Priority", stats["low_priority"])

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    priority_data = get_priority_distribution(filtered_df)
    if not priority_data.empty:
        fig_priority = px.pie(
            priority_data,
            names="Priority",
            values="count",
            title="Priority Distribution",
            color="Priority",
            color_discrete_map={"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"},
        )
        st.plotly_chart(fig_priority, use_container_width=True)

with chart_col2:
    status_data = get_status_breakdown(filtered_df)
    if not status_data.empty:
        fig_status = px.bar(
            status_data,
            x="Status",
            y="count",
            title="Status Breakdown",
            color="Status",
            color_discrete_map={
                "active": "#27ae60",
                "inactive": "#95a5a6",
                "lead": "#3498db",
                "churned": "#e74c3c",
            },
        )
        st.plotly_chart(fig_status, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    company_data = get_contacts_by_company(filtered_df)
    if not company_data.empty:
        fig_company = px.bar(
            company_data,
            x="Company",
            y="count",
            title="Contacts by Company",
            color="Company",
        )
        st.plotly_chart(fig_company, use_container_width=True)

with chart_col4:
    score_data = get_score_distribution(filtered_df)
    if not score_data.empty:
        fig_score = px.histogram(
            score_data,
            x="Score",
            nbins=20,
            title="Score Distribution",
            color_discrete_sequence=["#3498db"],
        )
        fig_score.update_layout(xaxis_title="Score", yaxis_title="Count")
        st.plotly_chart(fig_score, use_container_width=True)
