"""Trend velocity and spike detection logic."""

from typing import Dict, List


class TrendTracker:
    """Compute day-over-day keyword momentum."""

    def calculate_velocity(self, todays_kw: Dict[str, int], yesterdays_kw: Dict[str, int]) -> List[Dict[str, object]]:
        """Calculate keyword velocity between today and yesterday."""
        results: List[Dict[str, object]] = []

        for keyword, count in todays_kw.items():
            yesterday_count = yesterdays_kw.get(keyword, 0)
            today_count = count

            if yesterday_count == 0:
                velocity = 100.0 if today_count > 0 else 0.0
            else:
                velocity = ((today_count - yesterday_count) / yesterday_count) * 100

            direction = "rising" if velocity > 10 else "falling" if velocity < -10 else "stable"

            results.append(
                {
                    "keyword": keyword,
                    "today_count": today_count,
                    "yesterday_count": yesterday_count,
                    "velocity_percent": round(velocity, 1),
                    "is_spike": velocity > 50,
                    "direction": direction,
                }
            )

        results.sort(key=lambda item: abs(float(item["velocity_percent"])), reverse=True)
        return results[:10]
