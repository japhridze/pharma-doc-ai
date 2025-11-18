from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class BatchBase(BaseModel):
    filename: str
    text: str


class BatchCreate(BatchBase):
    pass


class BatchIssue(BaseModel):
    type: str
    message: str
    severity: str  # e.g. "low", "medium", "high"


class BatchOut(BaseModel):
    id: int
    filename: str
    risk_score: float
    issues_summary: str
    created_at: datetime
    issues: Optional[List[BatchIssue]] = []

    class Config:
        orm_mode = True
