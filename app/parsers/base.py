from abc import ABC, abstractmethod
from typing import List
from app.models.chat import Message

class ChatParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> List[Message]:
        pass

class ParseError(Exception):
    pass
