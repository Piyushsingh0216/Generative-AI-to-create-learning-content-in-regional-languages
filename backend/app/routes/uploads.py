import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.ai_usage import AIUsage
from app.models.upload import Upload
from app.models.user import User
from app.schemas.upload import UploadHistoryItem, UploadResponse
from app.services.analytics_service import derive_topics, update_user_topics
from app.services.extraction_service import SUPPORTED_EXTENSIONS, extract_text
from app.utils.exceptions import TextExtractionError, UnsupportedFileTypeError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/uploads", tags=["Uploads"])


def _save_upload_file(file: UploadFile) -> Path:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    upload_dir = Path(settings.upload_path)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}{extension}"
    target_path = upload_dir / safe_name
    target_path.write_bytes(file.file.read())
    return target_path


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    topic: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    try:
        stored_path = _save_upload_file(file)
        extracted = extract_text(stored_path)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TextExtractionError as exc:
        logger.exception("Text extraction failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected upload failure")
        raise HTTPException(status_code=500, detail="Upload failed.") from exc

    upload = Upload(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_path.name,
        file_type=stored_path.suffix.lower().replace(".", ""),
        topic=topic.strip() if topic else None,
        extracted_text=extracted,
    )
    db.add(upload)

    topics = derive_topics(extracted, explicit_topic=topic)
    update_user_topics(current_user, topics)

    db.add(AIUsage(user_id=current_user.id, action="upload", metadata_json={"file_type": upload.file_type}))
    db.commit()
    db.refresh(upload)

    return UploadResponse(
        id=upload.id,
        original_filename=upload.original_filename,
        stored_filename=upload.stored_filename,
        file_type=upload.file_type,
        topic=upload.topic,
        extracted_text_preview=upload.extracted_text[:1000],
        created_at=upload.created_at,
    )


@router.get("/history", response_model=list[UploadHistoryItem])
def upload_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(Upload)
        .filter(Upload.user_id == current_user.id)
        .order_by(Upload.created_at.desc())
        .all()
    )
    return items
