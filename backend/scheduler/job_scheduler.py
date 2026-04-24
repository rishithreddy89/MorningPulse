"""APScheduler-based daily scheduling for the intelligence pipeline."""

from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

import config


class JobScheduler:
    """Manage cron scheduling for daily digest generation."""

    def __init__(self, pipeline_fn: Callable[[], object]) -> None:
        """Create scheduler instance and store pipeline callback."""
        self.scheduler = BackgroundScheduler()
        self.pipeline_fn = pipeline_fn

    def start(self, run_now: bool = False) -> None:
        """Start the scheduler and optionally run the pipeline immediately."""
        self.scheduler.add_job(
            self.pipeline_fn,
            trigger="cron",
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
            id="daily_pulse",
        )
        self.scheduler.start()
        print(
            f"[JobScheduler] Scheduler running. Daily digest at "
            f"{config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}"
        )

        if run_now:
            print("[JobScheduler] Running pipeline immediately...")
            self.pipeline_fn()

    def stop(self) -> None:
        """Stop the scheduler if it is running."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[JobScheduler] Scheduler stopped")
