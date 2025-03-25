from src.database.models.review_step import ReviewStep, ReviewStepStatus
from src.database.enums import StepName
from src.database.crud.base import CRUDBase
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel


# Schemas for Create/Update operations
class ReviewStepCreate(BaseModel):
    review_id: int
    step_name: StepName
    input: Optional[str] = None
    status: Optional[ReviewStepStatus] = ReviewStepStatus.PENDING


class ReviewStepUpdate(BaseModel):
    input: Optional[str] = None
    output: Optional[str] = None
    status: Optional[ReviewStepStatus] = None


class CRUDReviewStep(CRUDBase[ReviewStep, ReviewStepCreate, ReviewStepUpdate]):
    def get_by_review_id(
        self, db: Session, *, review_id: int, skip: int = 0, limit: int = 100
    ) -> List[ReviewStep]:
        """Get steps for a specific review"""
        return (
            db.query(self.model)
            .filter(self.model.review_id == review_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name_and_review(
        self, db: Session, *, review_id: int, step_name: StepName
    ) -> Optional[ReviewStep]:
        """Get a specific step for a review by name"""
        return (
            db.query(self.model)
            .filter(
                self.model.review_id == review_id, self.model.step_name == step_name
            )
            .first()
        )

    def update_output(
        self, db: Session, *, step_id: int, output: str
    ) -> Optional[ReviewStep]:
        """Update the output and mark as completed"""
        step = self.get(db, id=step_id)
        if step:
            step.output = output
            step.status = ReviewStepStatus.COMPLETED
            step.updated_at = datetime.now()
            db.commit()
            db.refresh(step)
        return step


# Create a singleton instance
review_step = CRUDReviewStep(ReviewStep)
