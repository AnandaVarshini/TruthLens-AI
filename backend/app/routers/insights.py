"""Public model-insight endpoints backed by real, computed evaluation results."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..ml_service import ModelNotReadyError, model_service

router = APIRouter(prefix="/api", tags=["Model insights"])

CLASS_ORDER = ["Real", "Misleading", "Partially False", "Fake"]


@router.get("/insights")
def insights() -> dict:
    try:
        data = model_service.insights()
    except ModelNotReadyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation results could not be read.",
        )
    return data


@router.get("/model-info")
def model_info() -> dict:
    try:
        data = model_service.insights()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    selected = data.get("selected_model")
    candidates = data.get("candidates", {})
    return {
        "selected_model": selected,
        "selected_model_display_name": data.get("selected_model_display_name"),
        "selection_criterion": data.get("selection_criterion"),
        "classes": data.get("classes", CLASS_ORDER),
        "label_mapping": data.get("label_mapping", {}),
        "test_metrics": data.get("selected_model_metrics"),
        "features": data.get("features"),
        "generated_at": data.get("generated_at"),
        "candidates": {
            key: {
                "display_name": value.get("display_name"),
                "best_params": value.get("best_params"),
                "test": value.get("test"),
            }
            for key, value in candidates.items()
        },
    }
