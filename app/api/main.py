"""FastAPI REST API."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response as StarletteResponse

from app.schemas.api import (
    ErrorResponse,
    GroupsResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
    RankingsResponse,
    SimulateRequest,
    SimulateResponse,
    TeamsResponse,
)
from app.services.prediction import (
    PredictionService,
    RankingsService,
    SimulationService,
    TeamsService,
)
from monitoring.metrics import (
    API_ERRORS,
    MODEL_CONFIDENCE,
    SIMULATION_DURATION,
    SIMULATION_RUNS,
    get_metrics,
    track_prediction,
)
from src.config.settings import get_settings
from src.utils.exceptions import APIError, FifaPlatformError
from src.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

prediction_service = PredictionService()
simulation_service = SimulationService()
rankings_service = RankingsService()
teams_service = TeamsService()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    logger.info("api_starting", version=settings.app_version, env=settings.environment.value)
    yield
    logger.info("api_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="FIFA World Cup 2026 Prediction Platform API",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next: object) -> Response:
        response: Response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.exception_handler(FifaPlatformError)
    async def platform_error_handler(request: Request, exc: FifaPlatformError) -> JSONResponse:
        status = exc.status_code if isinstance(exc, APIError) else 500
        API_ERRORS.labels(endpoint=request.url.path, error_type=type(exc).__name__).inc()
        logger.error("api_error", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status,
            content=ErrorResponse(error=exc.message, details=exc.details).model_dump(),
        )

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health() -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            model_loaded=prediction_service.is_ready(),
        )

    @app.get("/metrics", tags=["Monitoring"])
    async def metrics() -> StarletteResponse:
        return StarletteResponse(content=get_metrics(), media_type="text/plain")

    @app.post("/predict", response_model=PredictResponse, tags=["Predictions"])
    @limiter.limit(get_settings().api_rate_limit)
    @track_prediction
    async def predict(request: Request, body: PredictRequest) -> PredictResponse:
        result = prediction_service.predict(body.home_team, body.away_team, neutral=body.neutral)
        MODEL_CONFIDENCE.set(result.confidence)
        return result

    @app.post("/simulate", response_model=SimulateResponse, tags=["Simulation"])
    @limiter.limit("10/minute")
    async def simulate(request: Request, body: SimulateRequest) -> SimulateResponse:
        start = time.perf_counter()
        try:
            result = simulation_service.simulate(body.n_simulations, body.seed)
            SIMULATION_RUNS.inc()
            return result
        finally:
            SIMULATION_DURATION.observe(time.perf_counter() - start)

    @app.get("/rankings", response_model=RankingsResponse, tags=["Rankings"])
    @limiter.limit(get_settings().api_rate_limit)
    async def rankings(
        request: Request,
        method: str = "model",
        since: str = "2024-01-01",
        pool_size: int = 48,
    ) -> RankingsResponse:
        return rankings_service.get_rankings(method=method, since=since, pool_size=pool_size)

    @app.get("/teams", response_model=TeamsResponse, tags=["Teams"])
    async def teams() -> TeamsResponse:
        return teams_service.get_teams()

    @app.get("/groups", response_model=GroupsResponse, tags=["Teams"])
    async def groups() -> GroupsResponse:
        return teams_service.get_groups()

    return app


app = create_app()


def run_server() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run_server()
