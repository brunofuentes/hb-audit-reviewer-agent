from sqlalchemy import Column, Integer, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base
from src.database.enums import StepName


class ReviewStep(Base):
    __tablename__ = "review_step"

    id = Column(Integer, primary_key=True, index=True)
    review = relationship("Review", back_populates="steps")
    name = Column(Enum(StepName), nullable=False)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
