from datetime import datetime
from typing import List

from pydantic import BaseModel


# ---------------------------------------------------------------------
# Batches: create / read models
# ---------------------------------------------------------------------
class BatchCreate(BaseModel):
    filename: str
    text: str


class BatchIssue(BaseModel):
    label: str
    detail: str
    severity: int


class BatchOut(BaseModel):
    id: int
    filename: str
    risk_score: float
    issues_summary: str
    created_at: datetime
    issues: List[BatchIssue] = []

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------
# Semantic search
# ---------------------------------------------------------------------
class BatchSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class BatchSearchResult(BaseModel):
    batch_id: int
    score: float
    text: str
