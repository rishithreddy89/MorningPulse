"""Digest storage adapter with local JSON and optional Supabase persistence."""

import glob
import json
import os
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from supabase import create_client

import config
from utils.logger import log_info, log_error, log_success


class Storage:
    """Persist and retrieve digest payloads from local disk and Supabase."""

    def __init__(self) -> None:
        """Initialize local output storage and optional Supabase client."""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        self.supabase = None

        try:
            if not config.SUPABASE_URL or not config.SUPABASE_KEY:
                raise ValueError("Missing Supabase credentials")
            self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            self.use_supabase = True
            log_success("Supabase connected")
        except Exception:
            self.use_supabase = False
            log_info("Supabase unavailable, using local storage")

    def _local_path(self, date_str: str) -> str:
        """Build the local digest file path for a given date key."""
        return f"{config.OUTPUT_DIR}digest_{date_str}.json"

    def save_digest(self, digest: Dict[str, Any]) -> bool:
        """Save digest to local JSON and optionally Supabase."""
        date_str = digest["date"]

        try:
            with open(self._local_path(date_str), "w", encoding="utf-8") as output_file:
                json.dump(digest, output_file, indent=2)
            log_success(f"Digest saved locally: {date_str}")
        except Exception as exc:
            log_error(f"Local save failed: {exc}")
            return False

        if self.use_supabase and self.supabase is not None:
            try:
                self.supabase.table("digests").upsert(
                    {
                        "date": date_str,
                        "content": digest,
                    },
                    on_conflict="date",
                ).execute()
                log_success(f"Digest saved to Supabase: {date_str}")
            except Exception as exc:
                log_error(f"Supabase save failed (non-critical): {exc}")

        return True

    def get_digest(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Load digest for a specific date."""
        path = self._local_path(date_str)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as input_file:
                    return json.load(input_file)
            except Exception as exc:
                log_error(f"Failed reading digest {date_str}: {exc}")
                return None
        return None

    def get_today_digest(self) -> Optional[Dict[str, Any]]:
        """Load today's digest by ISO date key, handling timestamp formats."""
        today = date.today().isoformat()
        
        # Try exact match first
        digest = self.get_digest(today)
        if digest:
            return digest
        
        # Try Supabase with LIKE query to handle timestamp format
        if self.use_supabase and self.supabase is not None:
            try:
                result = self.supabase.table("digests").select("*").like("date", f"{today}%").order("date", desc=True).limit(1).execute()
                if result.data and len(result.data) > 0:
                    return result.data[0].get("content")
            except Exception as exc:
                log_error(f"Supabase query failed: {exc}")
        
        return None

    def get_yesterday_digest(self) -> Optional[Dict[str, Any]]:
        """Load yesterday's digest by ISO date key."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        return self.get_digest(yesterday)

    def get_weekly_digests(self) -> List[Dict[str, Any]]:
        """Return last 7 days of digests sorted ascending by date."""
        results: List[Dict[str, Any]] = []
        for days_back in range(7, 0, -1):
            digest_date = (date.today() - timedelta(days=days_back)).isoformat()
            digest = self.get_digest(digest_date)
            if digest:
                results.append(digest)
        return results

    def get_all_dates(self) -> List[str]:
        """Return all dates that have saved digests."""
        files = glob.glob(f"{config.OUTPUT_DIR}digest_*.json")
        dates: List[str] = []
        for file_path in files:
            basename = os.path.basename(file_path)
            date_str = basename.replace("digest_", "").replace(".json", "")
            dates.append(date_str)
        return sorted(dates, reverse=True)
