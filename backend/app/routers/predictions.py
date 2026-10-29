"""Prediction, history and dashboard endpoints (all user-scoped)."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..ml_service import ModelNotReadyError, model_service
from ..models import Prediction, User
from ..schemas import (
    CategoryCount,
    ClassScore,
    DashboardStats,
    PredictionList,
    PredictionOut,
    PredictionRequest,
)

router = APIRouter(prefix="/api", tags=["Predictions"])


def _to_out(row: Prediction) -> PredictionOut:
    scores = None
    if row.scores_json:
        try:
            scores = [ClassScore(**item) for item in json.loads(row.scores_json)]
        except (ValueError, TypeError):
            scores = None
    return PredictionOut(
        id=row.id,
        text=row.text,
        label=row.label,
        confidence=row.confidence,
        score_type=row.score_type,
        scores=scores,
        model_name=row.model_name,
        created_at=row.created_at,
    )


@router.post("/predict", response_model=PredictionOut, status_code=status.HTTP_201_CREATED)
def predict(
    payload: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PredictionOut:
    try:
        result = model_service.predict(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except ModelNotReadyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction could not be completed. Please try again.",
        )

    row = Prediction(
        user_id=current_user.id,
        text=payload.text.strip(),
        label=result["label"],
        confidence=result["confidence"],
        score_type=result["score_type"],
        scores_json=json.dumps(result["scores"]),
        model_name=result["model_name"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.get("/predictions", response_model=PredictionList)
def list_predictions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PredictionList:
    base = select(Prediction).where(Prediction.user_id == current_user.id)
    total = db.scalar(
        select(func.count()).select_from(Prediction).where(Prediction.user_id == current_user.id)
    ) or 0
    rows = db.scalars(
        base.order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return PredictionList(
        total=int(total), limit=limit, offset=offset, items=[_to_out(row) for row in rows]
    )


@router.get("/predictions/stats", response_model=DashboardStats)
def stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardStats:
    total = db.scalar(
        select(func.count()).select_from(Prediction).where(Prediction.user_id == current_user.id)
    ) or 0
    grouped = db.execute(
        select(Prediction.label, func.count())
        .where(Prediction.user_id == current_user.id)
        .group_by(Prediction.label)
    ).all()
    counts = {label: int(count) for label, count in grouped}
    ordered = [CategoryCount(label=label, count=counts.get(label, 0)) for label in
               ("Real", "Misleading", "Partially False", "Fake")]
    recent = db.scalars(
        select(Prediction)
        .where(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(5)
    ).all()

    accuracy = None
    name = "unavailable"
    try:
        accuracy = model_service.metadata["selected_model_metrics"]["accuracy"]
        name = model_service.model_name()
    except Exception:
        pass

    return DashboardStats(
        total_predictions=int(total),
        counts_by_label=ordered,
        recent=[_to_out(row) for row in recent],
        model_name=name,
        model_accuracy_test=accuracy,
    )


@router.delete("/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    row = db.get(Prediction, prediction_id)
    if row is None or row.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")
    db.delete(row)
    db.commit()


@router.delete("/predictions", status_code=status.HTTP_200_OK)
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    rows = db.scalars(select(Prediction).where(Prediction.user_id == current_user.id)).all()
    for row in rows:
        db.delete(row)
    db.commit()
    return {"deleted": len(rows)}
