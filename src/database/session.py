from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

data_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
os.makedirs(data_dir, exist_ok=True)

db_path = os.path.join(data_dir, "audit_reviews.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize the database by creating all tables"""

    Base.metadata.create_all(engine)
    print(f"Database initialized successfully at {db_path}")


def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
