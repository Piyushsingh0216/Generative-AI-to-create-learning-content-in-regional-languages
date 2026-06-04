from typing import Dict

from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_users: int
    total_uploads: int
    total_summaries: int
    ai_usage_by_action: Dict[str, int]
