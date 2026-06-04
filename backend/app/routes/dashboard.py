from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.language_progress import LanguageProgress
from app.models.upload import Upload
from app.models.user import User
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    LanguageProgressItem,
    RecentUploadItem,
    TimeSpentRequest,
)
from app.services.gamification_service import calculate_level_progress_percent, reward_labels


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
LEARN_LANGUAGE_CARDS = [
    {"code": "hi", "label": "Hindi"},
    {"code": "bho", "label": "Bhojpuri"},
    {"code": "ta", "label": "Tamil"},
    {"code": "bn", "label": "Bengali"},
]


@router.get("/overview", response_model=DashboardOverviewResponse)
def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploads = (
        db.query(Upload)
        .filter(Upload.user_id == current_user.id)
        .order_by(Upload.created_at.desc())
        .all()
    )
    recent = [
        RecentUploadItem(
            id=item.id,
            original_filename=item.original_filename,
            file_type=item.file_type,
            created_at=item.created_at,
        )
        for item in uploads[:5]
    ]
    progress_rows = (
        db.query(LanguageProgress)
        .filter(LanguageProgress.user_id == current_user.id)
        .all()
    )
    progress_by_code = {item.language_code: item for item in progress_rows}
    language_progress = []
    for language in LEARN_LANGUAGE_CARDS:
        row = progress_by_code.get(language["code"])
        xp = row.xp if row else 0
        language_progress.append(
            LanguageProgressItem(
                language_code=language["code"],
                language_label=language["label"],
                xp=xp,
                streak=row.streak if row else 0,
                level=row.level if row else 1,
                level_progress_percent=calculate_level_progress_percent(xp),
                rewards=reward_labels(row.rewards if row else []),
            )
        )

    return DashboardOverviewResponse(
        total_uploads=len(uploads),
        total_summaries=current_user.summaries_generated,
        total_time_spent_seconds=current_user.time_spent_seconds,
        topics_learned=current_user.topics_learned or [],
        recent_uploads=recent,
        language_progress=language_progress,
    )


@router.post("/time-spent")
def track_time_spent(
    payload: TimeSpentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.time_spent_seconds += payload.seconds
    db.commit()
    return {"message": "Time updated.", "total_time_spent_seconds": current_user.time_spent_seconds}
