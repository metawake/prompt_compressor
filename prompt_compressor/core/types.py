from enum import Enum

class ContentType(Enum):
    """Types of content that can be analyzed"""
    TEXT = "text"
    QUESTION = "question"
    CODE = "code"
    COMMAND = "command"
    UNKNOWN = "unknown" 