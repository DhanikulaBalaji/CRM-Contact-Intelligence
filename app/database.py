"""Database layer providing SQLAlchemy ORM models and session management for contact persistence."""

from collections.abc import Generator

from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./crm_contacts.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    company_tier = Column(String(20), nullable=False)
    last_contacted_date = Column(Date, nullable=False)
    notes = Column(String(1000), nullable=True, default="")
    score = Column(Float, nullable=True, default=0.0)
    priority = Column(String(10), nullable=True, default="low", index=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
