from typing import List, Literal

from pydantic import BaseModel, Field


LessonQuestionType = Literal["mcq", "fill_blank", "match_words", "listening_text"]
LessonDifficulty = Literal["easy", "medium", "hard"]


class LessonQuestion(BaseModel):
    id: str
    type: LessonQuestionType
    prompt: str
    options: List[str] = Field(default_factory=list)
    answer: str
    listening_text: str | None = None
    difficulty: LessonDifficulty = "medium"
    focus_text: str | None = None
    is_review: bool = False


class LessonResponse(BaseModel):
    language_code: str
    language_label: str
    lesson_title: str
    difficulty: LessonDifficulty
    review_question_count: int = 0
    questions: List[LessonQuestion]


class LessonAnswerSubmission(BaseModel):
    question_id: str
    answer: str = Field(min_length=1, max_length=500)


class LessonCompletionRequest(BaseModel):
    language_code: str
    answers: List[LessonAnswerSubmission] = Field(default_factory=list)


class LessonCompletionResponse(BaseModel):
    language_code: str
    language_label: str
    difficulty: LessonDifficulty
    correct_answers: int
    total_questions: int
    base_xp: int
    bonus_xp: int
    earned_xp: int
    total_xp: int
    streak: int
    level: int
    level_progress_percent: int
    rewards: List[str]
    newly_unlocked_rewards: List[str]
    incorrect_focus_words: List[str]
