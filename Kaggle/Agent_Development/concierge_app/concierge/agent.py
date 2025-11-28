import json
import time
import google.generativeai as genai
from datetime import datetime
from typing import Any, Dict, List, Optional

from .core import Task, AgentResponse, Message, AgentState, ToolCall
from .config import LLMConfig

class ConciergeAgent:
    """Wrapper around Google Generative AI with enhanced capabilities."""
    
    def __init__(self, name: str, llm_config: LLMConfig, tools: Optional[List[Any]] = None):
        """
        Initialize a ConciergeAgent.
        
        Args:
            name: Unique identifier for the agent
            llm_config: Configuration for the LLM
            tools: Optional list of tools available to the agent
        """
        self.agent_id = name
        self.llm_config = llm_config
        self.tools: Dict[str, Any] = {}
        self.conversation_history: List[Message] = []
        self.context: Dict[str, Any] = {}
        
        # Initialize Google Generative AI model
        if llm_config.provider == 'gemini':
            if llm_config.api_key:
                genai.configure(api_key=llm_config.api_key)
                
            generation_config = {
                'temperature': llm_config.temperature,
                'max_output_tokens': llm_config.max_tokens,
            }
            self.model = genai.GenerativeModel(
                model_name=llm_config.model,
                generation_config=generation_config
            )
            self.chat = self.model.start_chat(history=[])
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")
        
        # Register tools if provided
        if tools:
            for tool in tools:
                self.add_tool(tool)
    
    def add_tool(self, tool: Any) -> None:
        """
        Register a tool with the agent.
        
        Args:
            tool: Tool instance to register
        """
        tool_name = getattr(tool, 'name', tool.__class__.__name__)
        self.tools[tool_name] = tool
    
    def execute(self, task: Task, session: Optional[Any] = None) -> AgentResponse:
        """
        Execute a task using the agent.
        
        Args:
            task: Task to execute
            session: Optional session for state management
            
        Returns:
            AgentResponse containing execution results
        """
        start_time = time.time()
        tool_calls: List[ToolCall] = []
        
        try:
            # Add task context to conversation history
            user_message = Message(
                role='user',
                content=task.description,
                timestamp=datetime.now(),
                metadata={'task_id': task.task_id, 'input_data': task.input_data}
            )
            self.conversation_history.append(user_message)
            
            # Prepare prompt with context
            prompt = task.description
            if task.input_data:
                prompt += f"\\n\\nInput Data: {json.dumps(task.input_data, indent=2)}"
            if task.context:
                prompt += f"\\n\\nContext: {json.dumps(task.context, indent=2)}"
            
            # Execute with LLM
            response = self.chat.send_message(prompt)
            output = response.text
            
            # Add response to conversation history
            assistant_message = Message(
                role='assistant',
                content=output,
                timestamp=datetime.now(),
                metadata={'task_id': task.task_id}
            )
            self.conversation_history.append(assistant_message)
            
            execution_time = time.time() - start_time
            
            return AgentResponse(
                task_id=task.task_id,
                agent_id=self.agent_id,
                output=output,
                tool_calls=tool_calls,
                execution_time=execution_time,
                status='success'
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResponse(
                task_id=task.task_id,
                agent_id=self.agent_id,
                output=None,
                tool_calls=tool_calls,
                execution_time=execution_time,
                status='error',
                error=e
            )
    
    def get_state(self) -> AgentState:
        """
        Get the current state of the agent.
        
        Returns:
            AgentState containing serializable state
        """
        return AgentState(
            agent_id=self.agent_id,
            conversation_history=self.conversation_history.copy(),
            tool_states={name: getattr(tool, 'state', {}) for name, tool in self.tools.items()},
            context=self.context.copy(),
            timestamp=datetime.now()
        )
    
    def restore_state(self, state: AgentState) -> None:
        """
        Restore agent state from a saved state.
        
        Args:
            state: AgentState to restore
        """
        self.conversation_history = state.conversation_history.copy()
        self.context = state.context.copy()
        
        # Restore tool states
        for tool_name, tool_state in state.tool_states.items():
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                if hasattr(tool, 'restore_state'):
                    tool.restore_state(tool_state)
        
        # Recreate chat with history
        if self.llm_config.provider == 'gemini':
            # Convert conversation history to Gemini format
            history = []
            for msg in self.conversation_history:
                if msg.role == 'user':
                    history.append({'role': 'user', 'parts': [msg.content]})
                elif msg.role == 'assistant':
                    history.append({'role': 'model', 'parts': [msg.content]})
            
            self.chat = self.model.start_chat(history=history)
