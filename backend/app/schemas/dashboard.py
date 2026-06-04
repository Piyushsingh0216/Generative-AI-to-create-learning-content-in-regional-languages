from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TimeSpentRequest(BaseModel):
    seconds: int = Field(gt=0, le=36000)


class RecentUploadItem(BaseModel):
    id: int
    original_filename: str
    file_type: str
    created_at: datetime


class LanguageProgressItem(BaseModel):
    language_code: str
    language_label: str
    xp: int
    streak: int
    level: int
    level_progress_percent: int
    rewards: List[str]


class DashboardOverviewResponse(BaseModel):
    total_uploads: int
    total_summaries: int
    total_time_spent_seconds: int
    topics_learned: List[str]
    recent_uploads: List[RecentUploadItem]
    language_progress: List[LanguageProgressItem]
