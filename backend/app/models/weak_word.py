from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class WeakWord(Base):
    __tablename__ = "weak_words"
    __table_args__ = (UniqueConstraint("user_id", "language_code", "question_id", name="uq_weak_word"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    language_code = Column(String(16), nullable=False, index=True)
    question_id = Column(String(64), nullable=False, index=True)
    focus_text = Column(String(255), nullable=False)

    incorrect_count = Column(Integer, default=0, nullable=False)
    last_attempted_at = Column(DateTime(timezone=True), nullable=True)
    last_incorrect_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="weak_words")
