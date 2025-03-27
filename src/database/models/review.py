from sqlalchemy import Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base
import enum


class ReviewStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"


class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    audit_url = Column(String(255), nullable=False)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    steps = relationship(
        "ReviewStep", back_populates="review", cascade="all, delete-orphan"
    )
