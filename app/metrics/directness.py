import re
from typing import List
from app.models.chat import Message, DirectnessMetric

class DirectnessAnalyzer:
    DEFLECTION_PATTERNS = [
        r'maybe',
        r'i guess',
        r'sort of',
        r'kind of',
        r'not sure',
        r'we\'ll see',
        r'later',
        r'eventually',
    ]
    
    def __init__(self, messages: List[Message]):
        self.messages = messages
        self.conversations = self._build_conversation_pairs()
    
    def _build_conversation_pairs(self):
        pairs = []
        i = 0
        while i < len(self.messages) - 1:
            current = self.messages[i]
            next_msg = self.messages[i + 1]
            
            if current.is_question and current.sender != next_msg.sender:
                pairs.append({
                    "question": current,
                    "answer": next_msg
                })
            i += 1
        
        return pairs
    
    def _is_deflection(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in self.DEFLECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def analyze(self) -> DirectnessMetric:
        if not self.conversations:
            return DirectnessMetric(
                score=0,
                confidence=0,
                questions_total=0,
                answers_direct=0,
                answers_deflected=0
            )
        
        total = len(self.conversations)
        deflected = sum(1 for pair in self.conversations if self._is_deflection(pair["answer"].text))
        direct = total - deflected
        
        score = (direct / total) * 10 if total > 0 else 0
        confidence = min(0.95, (total / 10) * 0.9)
        
        return DirectnessMetric(
            score=round(score, 1),
            confidence=round(confidence, 2),
            questions_total=total,
            answers_direct=direct,
            answers_deflected=deflected
        )
