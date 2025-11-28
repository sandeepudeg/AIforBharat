import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    """Configuration for LLM."""
    provider: str  # e.g., 'gemini', 'openai'
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv('GOOGLE_API_KEY')
