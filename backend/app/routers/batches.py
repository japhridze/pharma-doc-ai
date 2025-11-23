from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import schemas, models
from ..database import get_db

from ml.analyzer import analyze_batch_document
from ml.embeddings_store import add_embedding, search_embeddings

router = APIRouter(prefix="/batches", tags=["batches"])


# ---------------------------------------------------------------------
# Create batch
# ---------------------------------------------------------------------
@router.post("/", response_model=schemas.BatchOut)
async def create_batch(
    payload: schemas.BatchCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new batch document:
      1. Run heuristic analysis
      2. Save to SQL DB
      3. Store text embedding in local JSON vector store
    """
    analysis_result = analyze_batch_document(payload.text)

    batch = models.BatchDocument(
        filename=payload.filename,
        original_text=payload.text,
        risk_score=analysis_result.risk_score,
        issues_summary=analysis_result.summary,
    )

    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    # Save embedding for semantic search
    add_embedding(batch_id=batch.id, text=payload.text)

    # Map issues (dataclasses) → Pydantic models
    issues = [
        schemas.BatchIssue(
            label=i.label,
            detail=i.detail,
            severity=i.severity,
        )
        for i in analysis_result.issues
    ]

    return schemas.BatchOut(
        id=batch.id,
        filename=batch.filename,
        risk_score=batch.risk_score,
        issues_summary=batch.issues_summary,
        created_at=batch.created_at,
        issues=issues,
    )


# ---------------------------------------------------------------------
# List all batches
# ---------------------------------------------------------------------
@router.get("/", response_model=List[schemas.BatchOut])
async def list_batches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.BatchDocument))
    rows = result.scalars().all()

    return [
        schemas.BatchOut(
            id=row.id,
            filename=row.filename,
            risk_score=row.risk_score,
            issues_summary=row.issues_summary,
            created_at=row.created_at,
            issues=[],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------
# Get single batch
# ---------------------------------------------------------------------
@router.get("/{batch_id}", response_model=schemas.BatchOut)
async def get_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.BatchDocument).where(models.BatchDocument.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return schemas.BatchOut(
        id=batch.id,
        filename=batch.filename,
        risk_score=batch.risk_score,
        issues_summary=batch.issues_summary,
        created_at=batch.created_at,
        issues=[],
    )


# ---------------------------------------------------------------------
# Semantic search endpoint (vector store)
# ---------------------------------------------------------------------
@router.post("/search", response_model=List[schemas.BatchSearchResult])
async def search_batches(payload: schemas.BatchSearchRequest):
    """
    Semantic search over stored batch texts using our lightweight
    JSON-based vector store.
    """
    results = search_embeddings(payload.query, top_k=payload.top_k)

    return [
        schemas.BatchSearchResult(
            batch_id=r["batch_id"],
            score=r["score"],
            text=r["text"],
        )
        for r in results
    ]
