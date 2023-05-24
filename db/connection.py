from datetime import datetime
from sqlalchemy import create_engine, Integer, DateTime
from sqlalchemy.orm import Session, DeclarativeBase, mapped_column



DATABASE_URL = "sqlite:///main.sqlite"

engine = create_engine(DATABASE_URL, echo=True )

session = Session(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
  id = mapped_column(Integer(),primary_key=True, nullable=False)
  created = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
  updated = mapped_column(DateTime, onupdate=datetime.utcnow)


def initDB():
  Base.metadata.create_all(bind=engine)