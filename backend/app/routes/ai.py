import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.ai_usage import AIUsage
from app.models.summary import Summary
from app.models.upload import Upload
from app.models.user import User
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    QuestionRequest,
    QuestionResponse,
    SummarizeRequest,
    SummarizeResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.services.ai_service import ai_service
from app.services.translation_service import SUPPORTED_LANGUAGES, translate_text
from app.services.voice_service import synthesize_speech
from app.utils.exceptions import AIServiceError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI"])


def _resolve_input_text(
    db: Session,
    user_id: int,
    upload_id: int | None,
    raw_text: str | None,
) -> tuple[str, int | None]:
    if raw_text and raw_text.strip():
        return raw_text.strip(), upload_id

    if not upload_id:
        raise HTTPException(status_code=400, detail="Provide either upload_id or text.")

    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.user_id == user_id)
        .first()
    )
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found.")
    return upload.extracted_text, upload.id


@router.post("/translate", response_model=TranslateResponse)
def translate(
    payload: TranslateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported target language.")

    try:
        translated = translate_text(payload.text, payload.target_lang, payload.source_lang)
        audio_url = synthesize_speech(translated, payload.target_lang) if payload.enable_voice else None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Translation failed")
        raise HTTPException(status_code=500, detail="Translation failed.") from exc

    db.add(
        AIUsage(
            user_id=current_user.id,
            action="translate",
            metadata_json={"target_lang": payload.target_lang, "chars": len(payload.text)},
        )
    )
    db.commit()
    return TranslateResponse(translated_text=translated, language=payload.target_lang, audio_url=audio_url)


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(
    payload: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text, resolved_upload_id = _resolve_input_text(db, current_user.id, payload.upload_id, payload.text)
    try:
        summary_payload = ai_service.generate_summary(text)
        short_summary = str(summary_payload["short_summary"])
        bullet_points = [str(item) for item in summary_payload["bullet_points"]]

        if payload.target_lang != "en":
            short_summary = translate_text(short_summary, payload.target_lang, "auto")
            bullet_points = [translate_text(point, payload.target_lang, "auto") for point in bullet_points]

        audio_url = (
            synthesize_speech(short_summary, payload.target_lang) if payload.enable_voice else None
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Summary generation failed")
        raise HTTPException(status_code=500, detail="Summary generation failed.") from exc

    db.add(
        Summary(
            user_id=current_user.id,
            upload_id=resolved_upload_id,
            short_summary=short_summary,
            bullet_points=bullet_points,
        )
    )
    current_user.summaries_generated += 1
    db.add(
        AIUsage(
            user_id=current_user.id,
            action="summarize",
            metadata_json={"chars": len(text), "language": payload.target_lang},
        )
    )
    db.commit()

    return SummarizeResponse(
        short_summary=short_summary,
        bullet_points=bullet_points,
        language=payload.target_lang,
        audio_url=audio_url,
    )


@router.post("/questions", response_model=QuestionResponse)
def generate_questions(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text, _ = _resolve_input_text(db, current_user.id, payload.upload_id, payload.text)
    try:
        data = ai_service.generate_questions(text)
    except AIServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    db.add(
        AIUsage(
            user_id=current_user.id,
            action="questions",
            metadata_json={"chars": len(text)},
        )
    )
    db.commit()
    return QuestionResponse(**data)


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    context_text, _ = _resolve_input_text(db, current_user.id, payload.upload_id, payload.text)
    try:
        answer = ai_service.chat_with_context(
            payload.message,
            context_text=context_text,
            history=[item.model_dump() for item in payload.history],
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    db.add(
        AIUsage(
            user_id=current_user.id,
            action="chat",
            metadata_json={"chars": len(context_text), "message_chars": len(payload.message)},
        )
    )
    db.commit()
    return ChatResponse(answer=answer)
