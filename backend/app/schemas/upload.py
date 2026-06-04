from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_type: str
    topic: Optional[str]
    extracted_text_preview: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadHistoryItem(BaseModel):
    id: int
    original_filename: str
    file_type: str
    topic: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
