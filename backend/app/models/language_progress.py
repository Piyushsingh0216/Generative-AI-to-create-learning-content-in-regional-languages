from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class LanguageProgress(Base):
    __tablename__ = "language_progress"
    __table_args__ = (UniqueConstraint("user_id", "language_code", name="uq_user_language_progress"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    language_code = Column(String(16), nullable=False, index=True)

    xp = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    level = Column(Integer, default=1, nullable=False)
    lessons_completed = Column(Integer, default=0, nullable=False)
    rewards = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="language_progress_items")
