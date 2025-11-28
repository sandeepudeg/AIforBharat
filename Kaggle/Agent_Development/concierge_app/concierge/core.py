from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class Task:
    """Represents a task for an agent to execute."""
    task_id: str
    description: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """Record of a tool invocation."""
    tool_name: str
    params: Dict[str, Any]
    result: ToolResult
    execution_time: float


@dataclass
class AgentResponse:
    """Response from agent execution."""
    task_id: str
    agent_id: str
    output: Any
    tool_calls: List[ToolCall]
    execution_time: float
    status: str  # 'success', 'error', 'partial'
    error: Optional[Exception] = None


@dataclass
class Message:
    """Conversation message for history tracking."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Serializable agent state for persistence."""
    agent_id: str
    conversation_history: List[Message]
    tool_states: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            'agent_id': self.agent_id,
            'conversation_history': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'metadata': msg.metadata
                }
                for msg in self.conversation_history
            ],
            'tool_states': self.tool_states,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create state from dictionary."""
        return cls(
            agent_id=data['agent_id'],
            conversation_history=[
                Message(
                    role=msg['role'],
                    content=msg['content'],
                    timestamp=datetime.fromisoformat(msg['timestamp']),
                    metadata=msg.get('metadata', {})
                )
                for msg in data['conversation_history']
            ],
            tool_states=data['tool_states'],
            context=data['context'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
