"""Main application entry point of Ingestor"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.pipeline.scheduler import init_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestor")

scheduler = init_scheduler()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    # Startup: Start cron engine
    logger.info("Starting scheduler engine...")
    scheduler.start()
    yield
    # Shutdown: Gracefully stop and wait for active jobs to finish
    logger.info("Shutting down scheduler engine...")
    scheduler.shutdown(wait=True)


app = FastAPI(title="Ingestor Service", lifespan=lifespan)


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "healthy",
            "scheduler_running": scheduler.running,
            "active_jobs": [job.id for job in scheduler.get_jobs()],
        }
    )


# Manual trigger endpoint for testing without waiting for cron
@app.post("/jobs/crawl-now")
async def trigger_crawl_now() -> JSONResponse:
    job = scheduler.get_job("nightly_web_crawler")
    if job:
        job.modify(next_run_time=asyncio.get_event_loop().time())
        return JSONResponse(content={"message": "Crawler execution triggered"})
    return JSONResponse(status_code=404, content={"error": "Job not found"})
