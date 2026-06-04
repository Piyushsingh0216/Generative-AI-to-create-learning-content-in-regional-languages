from typing import List, Optional

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1)
    target_lang: str = Field(default="en")
    source_lang: str = Field(default="auto")
    enable_voice: bool = False


class TranslateResponse(BaseModel):
    translated_text: str
    language: str
    audio_url: Optional[str] = None


class SummarizeRequest(BaseModel):
    upload_id: Optional[int] = None
    text: Optional[str] = None
    target_lang: str = "en"
    enable_voice: bool = False


class SummarizeResponse(BaseModel):
    short_summary: str
    bullet_points: List[str]
    language: str
    audio_url: Optional[str] = None


class QuestionRequest(BaseModel):
    upload_id: Optional[int] = None
    text: Optional[str] = None


class MCQItem(BaseModel):
    question: str
    options: List[str]
    answer: str


class QuestionResponse(BaseModel):
    short_answer_questions: List[str]
    mcqs: List[MCQItem]


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    upload_id: Optional[int] = None
    text: Optional[str] = None
    message: str = Field(min_length=1)
    history: List[ChatHistoryItem] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
