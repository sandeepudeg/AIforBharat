"""
Storage and persistence system for game sessions and player profiles
Handles serialization, deserialization, and local storage operations
Requirements: 5.1, 5.2, 5.3, 5.4
"""

import json
import uuid
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from game_types import (
    GameSession,
    PlayerProfile,
    GameState,
    PerformanceMetrics,
    DifficultyLevel,
    Segment,
    Position,
    Obstacle,
    SkillAssessment,
)


class StorageManager:
    """Manages game session storage and player profile persistence"""

    STORAGE_KEY_PREFIX = "snake_adaptive_ai_"
    SESSIONS_KEY = f"{STORAGE_KEY_PREFIX}sessions"
    PROFILE_KEY = f"{STORAGE_KEY_PREFIX}profile"
    MAX_SESSIONS = 100  # Maximum sessions to store before pruning

    def __init__(self):
        """Initialize storage manager"""
        self.sessions_cache: Dict[str, GameSession] = {}
        self.profile_cache: Optional[PlayerProfile] = None
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Load sessions and profile from storage"""
        try:
            # Load sessions
            sessions_data = self._read_from_storage(self.SESSIONS_KEY)
            if sessions_data:
                for session_data in sessions_data:
                    session = self._deserialize_session(session_data)
                    self.sessions_cache[session.id] = session

            # Load profile
            profile_data = self._read_from_storage(self.PROFILE_KEY)
            if profile_data:
                self.profile_cache = self._deserialize_profile(profile_data)
            else:
                self.profile_cache = PlayerProfile()
        except Exception as e:
            print(f"Error loading from storage: {e}")
            self.sessions_cache = {}
            self.profile_cache = PlayerProfile()

    def _read_from_storage(self, key: str) -> Optional[Any]:
        """Read data from storage (simulated with in-memory dict)"""
        # In a real implementation, this would use localStorage or similar
        # For now, we use a simple in-memory storage
        if not hasattr(self, '_storage'):
            self._storage = {}
        return self._storage.get(key)

    def _write_to_storage(self, key: str, data: Any) -> None:
        """Write data to storage (simulated with in-memory dict)"""
        if not hasattr(self, '_storage'):
            self._storage = {}
        self._storage[key] = data

    def save_session(self, session: GameSession) -> None:
        """Save a game session to storage"""
        # Validate session
        if not self._validate_session(session):
            raise ValueError("Invalid game session")

        # Cache the session
        self.sessions_cache[session.id] = session

        # Update profile statistics
        self._update_profile_from_session(session)

        # Persist to storage
        self._persist_sessions()
        self._persist_profile()

        # Check if pruning is needed
        if len(self.sessions_cache) > self.MAX_SESSIONS:
            self._prune_sessions()

    def load_player_profile(self) -> PlayerProfile:
        """Load player profile from storage"""
        if self.profile_cache is None:
            self.profile_cache = PlayerProfile()
        return self.profile_cache

    def get_recent_sessions(self, count: int = 10) -> List[GameSession]:
        """Get the most recent N sessions"""
        sessions = list(self.sessions_cache.values())
        # Sort by timestamp descending
        sessions.sort(key=lambda s: s.timestamp, reverse=True)
        return sessions[:count]

    def get_sessions_by_score(self, count: int = 10) -> List[GameSession]:
        """Get sessions sorted by score (highest first)"""
        sessions = list(self.sessions_cache.values())
        sessions.sort(key=lambda s: s.score, reverse=True)
        return sessions[:count]

    def get_sessions_by_difficulty(self, difficulty_level: int) -> List[GameSession]:
        """Get sessions played at a specific difficulty level"""
        return [
            s for s in self.sessions_cache.values()
            if s.difficulty.level == difficulty_level
        ]

    def calculate_skill_trend(self) -> str:
        """Calculate skill trend from recent sessions"""
        recent = self.get_recent_sessions(5)
        if len(recent) < 2:
            return 'stable'

        # Compare average score of first half vs second half
        mid = len(recent) // 2
        if mid == 0:
            return 'stable'

        first_half_avg = sum(s.score for s in recent[:mid]) / len(recent[:mid])
        second_half_avg = sum(s.score for s in recent[mid:]) / len(recent[mid:])

        improvement = second_half_avg - first_half_avg

        if improvement > first_half_avg * 0.1:  # 10% improvement
            return 'improving'
        elif improvement < -first_half_avg * 0.1:  # 10% decline
            return 'declining'
        else:
            return 'stable'

    def get_best_score(self) -> int:
        """Get the best score from all sessions"""
        if not self.sessions_cache:
            return 0
        return max(s.score for s in self.sessions_cache.values())

    def get_average_survival_time(self) -> float:
        """Get average survival time across all sessions"""
        if not self.sessions_cache:
            return 0.0
        total_time = sum(s.duration for s in self.sessions_cache.values())
        return total_time / len(self.sessions_cache)

    def calculate_initial_difficulty(self) -> int:
        """Calculate initial difficulty for a new game based on history"""
        if not self.sessions_cache:
            return 1  # Start at difficulty 1

        recent = self.get_recent_sessions(5)
        if not recent:
            return 1

        # Average difficulty of recent sessions
        avg_difficulty = sum(s.difficulty.level for s in recent) / len(recent)

        # Round to nearest integer
        return max(1, min(10, round(avg_difficulty)))

    def _validate_session(self, session: GameSession) -> bool:
        """Validate a game session"""
        if not session.id:
            return False
        if session.score < 0:
            return False
        if session.duration < 0:
            return False
        if session.difficulty.level < 1 or session.difficulty.level > 10:
            return False
        return True

    def _update_profile_from_session(self, session: GameSession) -> None:
        """Update player profile with new session data"""
        if self.profile_cache is None:
            self.profile_cache = PlayerProfile()

        # Update best score
        if session.score > self.profile_cache.best_score:
            self.profile_cache.best_score = session.score

        # Update average survival time
        sessions = list(self.sessions_cache.values())
        if sessions:
            total_time = sum(s.duration for s in sessions)
            self.profile_cache.average_survival_time = total_time / len(sessions)

    def _persist_sessions(self) -> None:
        """Persist sessions to storage"""
        sessions_data = [
            self._serialize_session(session)
            for session in self.sessions_cache.values()
        ]
        self._write_to_storage(self.SESSIONS_KEY, sessions_data)

    def _persist_profile(self) -> None:
        """Persist profile to storage"""
        if self.profile_cache:
            profile_data = self._serialize_profile(self.profile_cache)
            self._write_to_storage(self.PROFILE_KEY, profile_data)

    def _prune_sessions(self) -> None:
        """Remove oldest sessions if storage quota exceeded"""
        sessions = list(self.sessions_cache.values())
        sessions.sort(key=lambda s: s.timestamp)

        # Keep only the most recent MAX_SESSIONS
        sessions_to_keep = sessions[-self.MAX_SESSIONS:]
        self.sessions_cache = {s.id: s for s in sessions_to_keep}

        self._persist_sessions()

    def _serialize_session(self, session: GameSession) -> Dict[str, Any]:
        """Serialize a game session to JSON-compatible dict"""
        return {
            'id': session.id,
            'score': session.score,
            'duration': session.duration,
            'difficulty': self._serialize_difficulty(session.difficulty),
            'metrics': self._serialize_metrics(session.metrics),
            'timestamp': session.timestamp,
        }

    def _deserialize_session(self, data: Dict[str, Any]) -> GameSession:
        """Deserialize a game session from dict"""
        return GameSession(
            id=data['id'],
            score=data['score'],
            duration=data['duration'],
            difficulty=self._deserialize_difficulty(data['difficulty']),
            metrics=self._deserialize_metrics(data['metrics']),
            timestamp=data['timestamp'],
        )

    def _serialize_difficulty(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Serialize difficulty level"""
        return {
            'level': difficulty.level,
            'speed': difficulty.speed,
            'obstacle_density': difficulty.obstacle_density,
            'food_spawn_rate': difficulty.food_spawn_rate,
            'adaptive_mode': difficulty.adaptive_mode,
        }

    def _deserialize_difficulty(self, data: Dict[str, Any]) -> DifficultyLevel:
        """Deserialize difficulty level"""
        return DifficultyLevel(
            level=data['level'],
            speed=data['speed'],
            obstacle_density=data['obstacle_density'],
            food_spawn_rate=data['food_spawn_rate'],
            adaptive_mode=data['adaptive_mode'],
        )

    def _serialize_metrics(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Serialize performance metrics"""
        return {
            'survival_time': metrics.survival_time,
            'food_consumed': metrics.food_consumed,
            'reaction_time': metrics.reaction_time,
            'collisions_avoided': metrics.collisions_avoided,
            'average_speed': metrics.average_speed,
            'timestamp': metrics.timestamp,
        }

    def _deserialize_metrics(self, data: Dict[str, Any]) -> PerformanceMetrics:
        """Deserialize performance metrics"""
        return PerformanceMetrics(
            survival_time=data['survival_time'],
            food_consumed=data['food_consumed'],
            reaction_time=data['reaction_time'],
            collisions_avoided=data['collisions_avoided'],
            average_speed=data['average_speed'],
            timestamp=data['timestamp'],
        )

    def _serialize_profile(self, profile: PlayerProfile) -> Dict[str, Any]:
        """Serialize player profile"""
        return {
            'best_score': profile.best_score,
            'average_survival_time': profile.average_survival_time,
        }

    def _deserialize_profile(self, data: Dict[str, Any]) -> PlayerProfile:
        """Deserialize player profile"""
        profile = PlayerProfile()
        profile.best_score = data.get('best_score', 0)
        profile.average_survival_time = data.get('average_survival_time', 0.0)
        return profile

    def clear_all_data(self) -> None:
        """Clear all stored data"""
        self.sessions_cache = {}
        self.profile_cache = PlayerProfile()
        self._write_to_storage(self.SESSIONS_KEY, [])
        self._write_to_storage(self.PROFILE_KEY, None)

    def get_session_by_id(self, session_id: str) -> Optional[GameSession]:
        """Get a specific session by ID"""
        return self.sessions_cache.get(session_id)

    def create_game_session(
        self,
        score: int,
        duration: int,
        difficulty: DifficultyLevel,
        metrics: PerformanceMetrics,
    ) -> GameSession:
        """Create a new game session"""
        session = GameSession(
            id=str(uuid.uuid4()),
            score=score,
            duration=duration,
            difficulty=difficulty,
            metrics=metrics,
            timestamp=int(time.time() * 1000),
        )
        return session
