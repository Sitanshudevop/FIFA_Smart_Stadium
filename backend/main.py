"""
main.py — FastAPI application entry point for Smart Stadium Operations.

Responsibilities:
  1. Validate environment configuration (fail-fast on missing secrets).
  2. Instantiate the FastAPI app with metadata.
  3. Configure CORS for the frontend.
  4. Mount the API router.
  5. Initialize the StadiumOrchestrator on startup.

Run with:  uvicorn backend.main:app --reload
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings

# ── Early Config Validation ───────────────────────────────────────────────────
# get_settings() triggers _enforce_required_env() which raises RuntimeError
# if GEMINI_API_KEY is missing or invalid.  This MUST happen before the app
# can serve any traffic.
try:
    settings = get_settings()
except RuntimeError as exc:
    logging.critical(str(exc))
    sys.exit(1)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s  %(name)-28s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("stadium_ops")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Initialize the orchestrator eagerly on startup so the first request
    doesn't pay cold-start latency.  Also validates that prompts.json
    and the GenAI client are loadable.
    """
    from backend.core.orchestrator import get_orchestrator

    try:
        orchestrator = get_orchestrator()
        cache_stats = await orchestrator.cache.stats()
        logger.info(
            "Orchestrator ready  model=%s  cache_entries=%d",
            settings.LLM_MODEL,
            cache_stats["alive_entries"],
        )
    except Exception as exc:
        # At this point GEMINI_API_KEY is validated, so this is an SDK issue
        logger.error(
            "Orchestrator startup failed — GenAI features will be "
            "unavailable: %s",
            exc,
        )
    yield
    logger.info("Shutting down Smart Stadium Ops")


# ── Delayed Router Import ────────────────────────────────────────────────────
# Import router AFTER settings are validated to prevent import-time failures
# when config is missing.
from backend.api.routes import router  # noqa: E402

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")

# ── Static Frontend (optional — for single-binary deploys) ────────────────────
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
