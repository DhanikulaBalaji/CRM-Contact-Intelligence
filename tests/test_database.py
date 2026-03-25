import pytest
from sqlalchemy import inspect
from app.database import init_db, engine, Base, SessionLocal, Contact, get_db


class TestInitDB:
    def test_creates_contacts_table(self):
        Base.metadata.drop_all(bind=engine)
        init_db()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "contacts" in tables

    def test_idempotent_call(self):
        init_db()
        init_db()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "contacts" in tables


class TestContactModel:
    def setup_method(self):
        Base.metadata.create_all(bind=engine)

    def teardown_method(self):
        Base.metadata.drop_all(bind=engine)

    def test_table_name(self):
        assert Contact.__tablename__ == "contacts"

    def test_create_contact(self):
        from datetime import date
        session = SessionLocal()
        try:
            contact = Contact(
                name="Test User",
                email="test@example.com",
                phone="555-0100",
                company="TestCorp",
                status="active",
                company_tier="enterprise",
                last_contacted_date=date(2025, 1, 15),
                notes="Test note",
                score=75.0,
                priority="high",
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)

            assert contact.id is not None
            assert contact.name == "Test User"
            assert contact.email == "test@example.com"
            assert contact.score == 75.0
            assert contact.priority == "high"
        finally:
            session.close()

    def test_email_uniqueness(self):
        from datetime import date
        session = SessionLocal()
        try:
            c1 = Contact(
                name="User A", email="dup@example.com", company="Corp",
                status="active", company_tier="startup",
                last_contacted_date=date(2025, 1, 1),
            )
            session.add(c1)
            session.commit()

            c2 = Contact(
                name="User B", email="dup@example.com", company="Corp",
                status="lead", company_tier="startup",
                last_contacted_date=date(2025, 1, 1),
            )
            session.add(c2)
            with pytest.raises(Exception):
                session.commit()
            session.rollback()
        finally:
            session.close()


class TestGetDB:
    def test_yields_session(self):
        gen = get_db()
        session = next(gen)
        assert session is not None
        try:
            next(gen)
        except StopIteration:
            pass

    def test_session_is_usable(self):
        init_db()
        gen = get_db()
        session = next(gen)
        result = session.execute(
            Contact.__table__.select()
        ).fetchall()
        assert isinstance(result, list)
        try:
            next(gen)
        except StopIteration:
            pass
