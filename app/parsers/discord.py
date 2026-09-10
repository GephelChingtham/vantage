import json
from datetime import datetime
from app.parsers.base import ChatParser, ParseError
from app.models.chat import Message

class DiscordParser(ChatParser):
    def parse(self, text: str) -> list[Message]:
        messages = []
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise ParseError("Invalid JSON format")
        
        for msg in data:
            if "content" not in msg or "author" not in msg:
                continue
            
            try:
                timestamp = datetime.fromisoformat(msg.get("timestamp", "2024-01-01T00:00:00").replace("Z", "+00:00"))
            except:
                timestamp = datetime.fromisoformat("2024-01-01T00:00:00")
            
            message = Message(
                sender=msg["author"].get("name", "Unknown"),
                text=msg.get("content", ""),
                timestamp=timestamp,
                length_words=len(msg.get("content", "").split()),
                is_question="?" in msg.get("content", "")
            )
            messages.append(message)
        
        return messages
