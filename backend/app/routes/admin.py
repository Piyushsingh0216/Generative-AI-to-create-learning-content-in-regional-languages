from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.ai_usage import AIUsage
from app.models.summary import Summary
from app.models.upload import Upload
from app.models.user import User
from app.schemas.admin import AdminStatsResponse


router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_uploads = db.query(func.count(Upload.id)).scalar() or 0
    total_summaries = db.query(func.count(Summary.id)).scalar() or 0

    usage_rows = db.query(AIUsage.action, func.count(AIUsage.id)).group_by(AIUsage.action).all()
    usage = {action: count for action, count in usage_rows}

    return AdminStatsResponse(
        total_users=total_users,
        total_uploads=total_uploads,
        total_summaries=total_summaries,
        ai_usage_by_action=usage,
    )
