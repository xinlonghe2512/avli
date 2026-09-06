import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.pipeline.crawler import scrape_target
from app.pipeline.vector_store import process_and_ingest

logger = logging.getLogger("ingestor")
scheduler = AsyncIOScheduler()


async def run_ingestion_pipeline():
    targets = [
        "https://example.com/docs",
        "https://example.com/blog",
    ]

    logger.info("Starting ingestion cycle...")
    for url in targets:
        try:
            logger.info(f"Crawling: {url}")
            content = await scrape_target(url)
            await process_and_ingest(content, source_url=url)
        except Exception as e:
            logger.error(f"Failed to ingest {url}: {e}", exc_info=True)

    logger.info("Ingestion cycle complete.")


def init_scheduler():
    # Runs every day at 02:00 UTC (cron expression)
    scheduler.add_job(
        run_ingestion_pipeline,
        trigger=CronTrigger(hour=2, minute=0, timezone="UTC"),
        id="nightly_web_crawler",
        name="Scrape web sources and ingest into VectorDB",
        max_instances=1,  # Prevents overlap if crawl takes long
        coalesce=True,  # Merges missed runs if the system was paused
    )
    return scheduler
