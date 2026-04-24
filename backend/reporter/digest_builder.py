"""Build the final digest payload returned by the API."""

from typing import Any, Dict


class DigestBuilder:
    """Assemble all processed intelligence into one digest object."""

    def build(self, gemini_output: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Assemble the EdTech digest payload with only required fields."""
        return {
            "date": date_str,
            "competitor_updates": gemini_output.get("competitor_updates", []),
            "user_pain_points": gemini_output.get("user_pain_points", []),
            "emerging_tech_trends": gemini_output.get("emerging_tech_trends", []),
        }
