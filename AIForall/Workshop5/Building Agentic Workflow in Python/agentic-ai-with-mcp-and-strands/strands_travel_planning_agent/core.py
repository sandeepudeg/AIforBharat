"""
Core interfaces and base classes for the Travel Planning Agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentRequest:
    """Represents a request from Travel_Planner to a specialized agent."""
    
    source: str  # "travel_planner"
    target: str  # Agent name (e.g., "weather_agent")
    action: str  # Action to perform (e.g., "get_forecast")
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


@dataclass
class AgentResponse:
    """Represents a response from a specialized agent to Travel_Planner."""
    
    source: str  # Agent name
    target: str  # "travel_planner"
    status: str  # "success" or "error"
    data: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = ""


class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for the agent."""
        import logging
        logger = logging.getLogger(self.name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.name}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request from Travel_Planner.
        
        Args:
            request: AgentRequest with action and parameters
            
        Returns:
            AgentResponse with status and data
        """
        pass
    
    def _create_response(
        self,
        status: str,
        data: Dict[str, Any],
        error_message: Optional[str] = None,
        request_id: str = ""
    ) -> AgentResponse:
        """Helper to create a response."""
        return AgentResponse(
            source=self.name,
            target="travel_planner",
            status=status,
            data=data,
            error_message=error_message,
            request_id=request_id
        )
    
    def _log_request(self, request: AgentRequest):
        """Log incoming request."""
        self.logger.info(f"Received request: {request.action}")
    
    def _log_response(self, response: AgentResponse):
        """Log outgoing response."""
        self.logger.info(f"Sending response: {response.status}")


class TravelPlannerInterface(ABC):
    """Interface for the Travel_Planner orchestrator."""
    
    @abstractmethod
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query and extract parameters."""
        pass
    
    @abstractmethod
    def route_to_agents(self, parameters: Dict[str, Any]) -> List[AgentRequest]:
        """Determine which agents are needed and create requests."""
        pass
    
    @abstractmethod
    def aggregate_responses(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Combine responses from all agents."""
        pass
    
    @abstractmethod
    def coordinate_agents(self, initial_results: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with dependent agents (Budget, Visa, Transport)."""
        pass
    
    @abstractmethod
    def format_response(self, aggregated_data: Dict[str, Any]) -> str:
        """Format final response for user."""
        pass


class AgentRegistry:
    """Registry for managing all agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    def list_agents(self) -> List[str]:
        """List all agent names."""
        return list(self.agents.keys())


class MessageBroker:
    """Handles message passing between agents and Travel_Planner."""
    
    def __init__(self):
        self.message_queue: List[Dict[str, Any]] = []
        self.message_history: List[Dict[str, Any]] = []
    
    def send_request(self, request: AgentRequest) -> None:
        """Send a request to an agent."""
        message = {
            "type": "request",
            "content": request,
            "timestamp": datetime.now()
        }
        self.message_queue.append(message)
        self.message_history.append(message)
    
    def send_response(self, response: AgentResponse) -> None:
        """Send a response from an agent."""
        message = {
            "type": "response",
            "content": response,
            "timestamp": datetime.now()
        }
        self.message_queue.append(message)
        self.message_history.append(message)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in queue."""
        return self.message_queue.copy()
    
    def clear_queue(self) -> None:
        """Clear the message queue."""
        self.message_queue.clear()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get message history."""
        return self.message_history.copy()


class ErrorHandler:
    """Handles errors and provides fallbacks."""
    
    @staticmethod
    def handle_timeout(agent_name: str, action: str) -> AgentResponse:
        """Handle API timeout."""
        return AgentResponse(
            source=agent_name,
            target="travel_planner",
            status="error",
            data={},
            error_message=f"Timeout while performing {action}. Please try manual search."
        )
    
    @staticmethod
    def handle_invalid_input(agent_name: str, field: str, value: Any) -> AgentResponse:
        """Handle invalid input."""
        return AgentResponse(
            source=agent_name,
            target="travel_planner",
            status="error",
            data={},
            error_message=f"Invalid {field}: {value}"
        )
    
    @staticmethod
    def handle_api_error(agent_name: str, api_name: str, error: str) -> AgentResponse:
        """Handle API error."""
        return AgentResponse(
            source=agent_name,
            target="travel_planner",
            status="error",
            data={},
            error_message=f"{api_name} API error: {error}"
        )


class ValidationHelper:
    """Helper for validating inputs."""
    
    @staticmethod
    def validate_destination(destination: str) -> bool:
        """Validate destination is not empty."""
        return destination and len(destination.strip()) > 0
    
    @staticmethod
    def validate_dates(start_date: str, end_date: str) -> bool:
        """Validate date format and range."""
        try:
            from datetime import datetime
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            return start < end
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_budget(budget: float) -> bool:
        """Validate budget is positive."""
        return isinstance(budget, (int, float)) and budget > 0
    
    @staticmethod
    def validate_age(age: int) -> bool:
        """Validate age is reasonable."""
        return isinstance(age, int) and 0 < age < 150


class CurrencyConverter:
    """Handles currency conversion."""
    
    # Mock exchange rates (in production, fetch from API)
    EXCHANGE_RATES = {
        "USD_EUR": 0.92,
        "EUR_USD": 1.09,
        "USD_GBP": 0.79,
        "GBP_USD": 1.27,
        "EUR_GBP": 0.86,
        "GBP_EUR": 1.16,
    }
    
    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another."""
        if from_currency == to_currency:
            return amount
        
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key not in cls.EXCHANGE_RATES:
            raise ValueError(f"Conversion not supported: {from_currency} to {to_currency}")
        
        rate = cls.EXCHANGE_RATES[rate_key]
        return round(amount * rate, 2)
    
    @classmethod
    def get_rate(cls, from_currency: str, to_currency: str) -> float:
        """Get exchange rate."""
        if from_currency == to_currency:
            return 1.0
        
        rate_key = f"{from_currency}_{to_currency}"
        return cls.EXCHANGE_RATES.get(rate_key, 1.0)


class MemoryService:
    """Handles user preferences and trip history."""
    
    def __init__(self):
        self.user_preferences: Dict[str, Any] = {}
        self.trip_history: List[Dict[str, Any]] = []
    
    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Save user preferences."""
        self.user_preferences[user_id] = preferences
    
    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        return self.user_preferences.get(user_id)
    
    def save_trip(self, user_id: str, trip: Dict[str, Any]) -> None:
        """Save completed trip."""
        self.trip_history.append({
            "user_id": user_id,
            "trip": trip,
            "timestamp": datetime.now()
        })
    
    def get_trip_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's trip history."""
        return [
            item["trip"] for item in self.trip_history
            if item["user_id"] == user_id
        ]
