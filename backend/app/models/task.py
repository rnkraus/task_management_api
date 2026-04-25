from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from app.core.db import Base
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, nullable=False, default=3)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tasks")