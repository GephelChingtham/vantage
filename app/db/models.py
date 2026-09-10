from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class AnalysisJobDB(Base):
    __tablename__ = "analysis_jobs"
    
    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    status = Column(String, default="processing")
    
    directness_score = Column(Float, nullable=True)
    effort_matrix = Column(JSON, nullable=True)
    red_flags = Column(JSON, nullable=True)
    post_mortem = Column(JSON, nullable=True)
    
    source_format = Column(String)
    message_count = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    is_deleted = Column(Boolean, default=False)

class UserDB(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
