from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True, index=True)

    short_summary = Column(Text, nullable=False)
    bullet_points = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="summaries")
    upload = relationship("Upload", back_populates="summaries")
