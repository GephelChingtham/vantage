from typing import List
from app.models.chat import Message, EffortMatrix

class EffortAnalyzer:
    def __init__(self, messages: List[Message]):
        self.messages = messages
        self.by_sender = self._group_by_sender()
    
    def _group_by_sender(self) -> dict:
        by_sender = {}
        for msg in self.messages:
            if msg.sender not in by_sender:
                by_sender[msg.sender] = []
            by_sender[msg.sender].append(msg)
        return by_sender
    
    def _calculate_initiation_ratio(self) -> tuple[float, float]:
        senders = list(self.by_sender.keys())
        if len(senders) != 2:
            return 0.5, 0.5
        
        person_a, person_b = senders[0], senders[1]
        person_a_msgs = len(self.by_sender[person_a])
        person_b_msgs = len(self.by_sender[person_b])
        
        total = person_a_msgs + person_b_msgs
        return (round(person_a_msgs / total, 2), round(person_b_msgs / total, 2))
    
    def _calculate_reply_delay(self) -> tuple[float, float]:
        senders = list(self.by_sender.keys())
        if len(senders) != 2:
            return 0, 0
        
        person_a, person_b = senders[0], senders[1]
        delays_a = []
        delays_b = []
        
        for i in range(len(self.messages) - 1):
            current = self.messages[i]
            next_msg = self.messages[i + 1]
            
            if current.sender != next_msg.sender:
                delay_hours = (next_msg.timestamp - current.timestamp).total_seconds() / 3600
                
                if current.sender == person_a:
                    delays_b.append(delay_hours)
                else:
                    delays_a.append(delay_hours)
        
        avg_delay_a = sum(delays_a) / len(delays_a) if delays_a else 0
        avg_delay_b = sum(delays_b) / len(delays_b) if delays_b else 0
        
        return (round(avg_delay_a, 1), round(avg_delay_b, 1))
    
    def _calculate_message_length(self) -> tuple[int, int]:
        senders = list(self.by_sender.keys())
        if len(senders) != 2:
            return 0, 0
        
        person_a, person_b = senders[0], senders[1]
        
        avg_len_a = sum(len(msg.text.split()) for msg in self.by_sender[person_a]) / len(self.by_sender[person_a]) if self.by_sender[person_a] else 0
        avg_len_b = sum(len(msg.text.split()) for msg in self.by_sender[person_b]) / len(self.by_sender[person_b]) if self.by_sender[person_b] else 0
        
        return (int(avg_len_a), int(avg_len_b))
    
    def analyze(self) -> EffortMatrix:
        initiator_a, initiator_b = self._calculate_initiation_ratio()
        delay_a, delay_b = self._calculate_reply_delay()
        len_a, len_b = self._calculate_message_length()
        
        return EffortMatrix(
            initiator_person_a=initiator_a,
            initiator_person_b=initiator_b,
            avg_reply_delay_person_a_hours=delay_a,
            avg_reply_delay_person_b_hours=delay_b,
            avg_message_length_person_a=len_a,
            avg_message_length_person_b=len_b
        )
