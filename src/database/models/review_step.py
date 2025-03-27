from sqlalchemy import Column, Integer, Enum, Text, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base
from src.database.enums import StepName


class ReviewStep(Base):
    __tablename__ = "review_step"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)
    review = relationship("Review", back_populates="steps")
    name = Column(Enum(StepName), nullable=False)
    llm_model = Column(String(255), nullable=True)
    input = Column(Text, nullable=True)
    output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
