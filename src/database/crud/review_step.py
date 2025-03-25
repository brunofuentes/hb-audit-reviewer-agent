from src.database.models.review_step import ReviewStep
from src.database.enums import StepName
from src.database.crud.base import CRUDBase
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel


class ReviewStepCreate(BaseModel):
    review_id: int
    name: StepName
    input: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


class ReviewStepUpdate(BaseModel):
    input: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


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
        self, db: Session, *, review_id: int, name: StepName
    ) -> Optional[ReviewStep]:
        """Get a specific step for a review by name"""
        return (
            db.query(self.model)
            .filter(self.model.review_id == review_id, self.model.name == name)
            .first()
        )

    def update_output(
        self, db: Session, *, step_id: int, output: Dict[str, Any]
    ) -> Optional[ReviewStep]:
        """Update the output and mark as completed"""
        step = self.get(db, id=step_id)
        if step:
            step.output = output
            step.updated_at = datetime.now()
            db.commit()
            db.refresh(step)
        return step


review_step = CRUDReviewStep(ReviewStep)
