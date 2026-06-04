from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    time_spent_seconds = Column(Integer, default=0, nullable=False)
    summaries_generated = Column(Integer, default=0, nullable=False)
    topics_learned = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")
    ai_usages = relationship("AIUsage", back_populates="user", cascade="all, delete-orphan")
    language_progress_items = relationship(
        "LanguageProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    weak_words = relationship("WeakWord", back_populates="user", cascade="all, delete-orphan")
