from typing import List
from ml.analyzer import analyze_batch_document


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import schemas, models
from ..database import get_db
from ml.analyzer import analyze_batch_document

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("/", response_model=schemas.BatchOut)
async def create_batch(
    payload: schemas.BatchCreate,
    db: AsyncSession = Depends(get_db),
):
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

    return schemas.BatchOut(
        id=batch.id,
        filename=batch.filename,
        risk_score=batch.risk_score,
        issues_summary=batch.issues_summary,
        created_at=batch.created_at,
        issues=analysis_result.issues,
    )


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
            issues=[],  # later: load detailed issues from separate table or vector store
        )
        for row in rows
    ]


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
