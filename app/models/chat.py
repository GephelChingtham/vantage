from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    sender: str
    text: str
    timestamp: datetime
    length_words: int = 0
    is_question: bool = False

class DirectnessMetric(BaseModel):
    score: float
    confidence: float
    questions_total: int
    answers_direct: int
    answers_deflected: int

class EffortMatrix(BaseModel):
    initiator_person_a: float
    initiator_person_b: float
    avg_reply_delay_person_a_hours: float
    avg_reply_delay_person_b_hours: float
    avg_message_length_person_a: int
    avg_message_length_person_b: int

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    directness_score: Optional[float] = None
    directness_confidence: Optional[float] = None
    effort_matrix: Optional[dict] = None
    red_flags: Optional[dict] = None
    post_mortem: Optional[dict] = None
