from src.database.models.review import Review, ReviewStatus
from src.database.crud.base import CRUDBase
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel


# Schemas for Create/Update operations
class ReviewCreate(BaseModel):
    audit_url: str
    status: ReviewStatus = ReviewStatus.PENDING


class ReviewUpdate(BaseModel):
    audit_url: Optional[str] = None
    audit_date: Optional[datetime] = None
    status: Optional[ReviewStatus] = None


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def get_by_status(
        self, db: Session, *, status: ReviewStatus, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        """Get reviews by status"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self, db: Session, *, review_id: int, status: ReviewStatus
    ) -> Optional[Review]:
        """Update only the status of a review"""
        review = self.get(db, id=review_id)
        if review:
            review.status = status
            review.updated_at = datetime.now()
            db.commit()
            db.refresh(review)
        return review


review = CRUDReview(Review)
