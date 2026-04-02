from fastapi import APIRouter, Depends

from app.api.dependencies import get_metrics_service
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def get_metrics(metrics_service: MetricsService = Depends(get_metrics_service)) -> MetricsResponse:
    return MetricsResponse(counters=metrics_service.snapshot())
