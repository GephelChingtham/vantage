import re
from datetime import datetime
from app.parsers.base import ChatParser, ParseError
from app.models.chat import Message

class WhatsAppParser(ChatParser):
    PATTERN = r"\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*(?:AM|PM)?)\]\s*(.+?):\s*(.+)"
    
    def parse(self, text: str) -> list[Message]:
        messages = []
        for line in text.split("\n"):
            match = re.match(self.PATTERN, line)
            if not match:
                continue
            
            date_str, time_str, sender, content = match.groups()
            
            try:
                timestamp_str = f"{date_str} {time_str}"
                timestamp = datetime.strptime(timestamp_str, "%m/%d/%y %I:%M %p")
            except ValueError:
                continue
            
            message = Message(
                sender=sender.strip(),
                text=content.strip(),
                timestamp=timestamp,
                length_words=len(content.split()),
                is_question="?" in content
            )
            messages.append(message)
        
        return messages
