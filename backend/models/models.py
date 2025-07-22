from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.db import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_done = Column(Boolean, default=False)
    start = Column(String, nullable=True)      # ISO datetime string
    end = Column(String, nullable=True)        # ISO datetime string
    priority = Column(Integer, nullable=True)  # 1 (high) - 4 (low) or similar
    urgency = Column(Integer, nullable=True)   # 1 (urgent) - 4 (not urgent)
    feedback = Column(String, nullable=True)   # User feedback/comments

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    rating = Column(Integer, nullable=True)  # 1 (bad) to 5 (good)
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
