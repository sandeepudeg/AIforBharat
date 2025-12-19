"""
Statistics Screen Component
Displays historical game data including best score, average survival time,
skill progression, and difficulty evolution
Requirements: 5.2, 5.3
"""

from typing import List, Optional, Dict, Any
from storage_manager import StorageManager
from game_types import GameSession, PerformanceMetrics


class StatisticsScreen:
    """Displays player statistics and game history"""

    def __init__(self, storage_manager: Optional[StorageManager] = None):
        """Initialize statistics screen with storage manager"""
        if storage_manager is None:
            storage_manager = StorageManager()
        self.storage_manager = storage_manager

    def get_best_score(self) -> int:
        """Get the best score from all sessions"""
        return self.storage_manager.get_best_score()

    def get_average_survival_time(self) -> float:
        """Get average survival time across all sessions"""
        return self.storage_manager.get_average_survival_time()

    def get_skill_progression(self) -> List[Dict[str, Any]]:
        """
        Get skill progression data from recent sessions
        Returns list of skill assessments with timestamps
        """
        recent_sessions = self.storage_manager.get_recent_sessions(10)
        
        progression = []
        for session in reversed(recent_sessions):  # Oldest first
            progression.append({
                'timestamp': session.timestamp,
                'score': session.score,
                'duration': session.duration,
                'difficulty_level': session.difficulty.level,
                'food_consumed': session.metrics.food_consumed,
            })
        
        return progression

    def get_difficulty_evolution(self) -> List[Dict[str, Any]]:
        """
        Get difficulty evolution across games
        Returns list of difficulty levels with timestamps
        """
        recent_sessions = self.storage_manager.get_recent_sessions(10)
        
        evolution = []
        for session in reversed(recent_sessions):  # Oldest first
            evolution.append({
                'timestamp': session.timestamp,
                'difficulty_level': session.difficulty.level,
                'speed': session.difficulty.speed,
                'obstacle_density': session.difficulty.obstacle_density,
                'food_spawn_rate': session.difficulty.food_spawn_rate,
                'adaptive_mode': session.difficulty.adaptive_mode,
            })
        
        return evolution

    def get_session_count(self) -> int:
        """Get total number of sessions played"""
        return len(self.storage_manager.sessions_cache)

    def get_total_playtime(self) -> int:
        """Get total playtime in seconds across all sessions"""
        sessions = list(self.storage_manager.sessions_cache.values())
        return sum(s.duration for s in sessions)

    def get_average_score(self) -> float:
        """Get average score across all sessions"""
        sessions = list(self.storage_manager.sessions_cache.values())
        if not sessions:
            return 0.0
        return sum(s.score for s in sessions) / len(sessions)

    def get_skill_trend(self) -> str:
        """Get current skill trend (improving, stable, declining)"""
        return self.storage_manager.calculate_skill_trend()

    def get_highest_difficulty_reached(self) -> int:
        """Get the highest difficulty level reached"""
        sessions = list(self.storage_manager.sessions_cache.values())
        if not sessions:
            return 0
        return max(s.difficulty.level for s in sessions)

    def get_average_difficulty(self) -> float:
        """Get average difficulty level across all sessions"""
        sessions = list(self.storage_manager.sessions_cache.values())
        if not sessions:
            return 0.0
        return sum(s.difficulty.level for s in sessions) / len(sessions)

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get complete statistics summary"""
        return {
            'best_score': self.get_best_score(),
            'average_score': self.get_average_score(),
            'average_survival_time': self.get_average_survival_time(),
            'session_count': self.get_session_count(),
            'total_playtime': self.get_total_playtime(),
            'skill_trend': self.get_skill_trend(),
            'highest_difficulty': self.get_highest_difficulty_reached(),
            'average_difficulty': self.get_average_difficulty(),
        }

    def render_statistics_display(self) -> str:
        """Render the statistics screen as a formatted string"""
        lines = []
        
        lines.append("=" * 50)
        lines.append("STATISTICS SCREEN".center(50))
        lines.append("=" * 50)
        lines.append("")
        
        # Overall Statistics
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 50)
        lines.append(f"Sessions Played:        {self.get_session_count()}")
        lines.append(f"Total Playtime:         {self._format_time(self.get_total_playtime())}")
        lines.append(f"Best Score:             {self.get_best_score()}")
        lines.append(f"Average Score:          {self.get_average_score():.1f}")
        lines.append(f"Average Survival Time:  {self.get_average_survival_time():.1f}s")
        lines.append("")
        
        # Skill Progression
        lines.append("SKILL PROGRESSION")
        lines.append("-" * 50)
        lines.append(f"Current Trend:          {self.get_skill_trend().upper()}")
        lines.append(f"Highest Difficulty:     {self.get_highest_difficulty_reached()}/10")
        lines.append(f"Average Difficulty:     {self.get_average_difficulty():.1f}/10")
        lines.append("")
        
        # Recent Sessions
        lines.append("RECENT SESSIONS (Last 5)")
        lines.append("-" * 50)
        recent_sessions = self.storage_manager.get_recent_sessions(5)
        if recent_sessions:
            for i, session in enumerate(recent_sessions, 1):
                lines.append(
                    f"{i}. Score: {session.score:4d} | "
                    f"Time: {session.duration:3d}s | "
                    f"Difficulty: {session.difficulty.level}/10"
                )
        else:
            lines.append("No sessions yet")
        lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)

    def render_skill_progression_chart(self) -> str:
        """Render skill progression as a simple text chart"""
        lines = []
        
        lines.append("SKILL PROGRESSION CHART")
        lines.append("-" * 50)
        
        progression = self.get_skill_progression()
        if not progression:
            lines.append("No data available")
            return "\n".join(lines)
        
        # Find max score for scaling
        max_score = max(p['score'] for p in progression) if progression else 1
        if max_score == 0:
            max_score = 1
        
        for i, data in enumerate(progression[-10:]):  # Show last 10
            score = data['score']
            bar_length = int((score / max_score) * 30)
            bar = "█" * bar_length
            lines.append(f"Game {i+1:2d}: {bar:<30} {score:4d}")
        
        lines.append("")
        
        return "\n".join(lines)

    def render_difficulty_evolution_chart(self) -> str:
        """Render difficulty evolution as a simple text chart"""
        lines = []
        
        lines.append("DIFFICULTY EVOLUTION CHART")
        lines.append("-" * 50)
        
        evolution = self.get_difficulty_evolution()
        if not evolution:
            lines.append("No data available")
            return "\n".join(lines)
        
        for i, data in enumerate(evolution[-10:]):  # Show last 10
            difficulty = data['difficulty_level']
            bar = "▓" * difficulty + "░" * (10 - difficulty)
            lines.append(f"Game {i+1:2d}: [{bar}] Level {difficulty}/10")
        
        lines.append("")
        
        return "\n".join(lines)

    def render_full_statistics_display(self) -> str:
        """Render complete statistics display with all charts"""
        lines = []
        
        lines.append(self.render_statistics_display())
        lines.append("")
        lines.append(self.render_skill_progression_chart())
        lines.append("")
        lines.append(self.render_difficulty_evolution_chart())
        
        return "\n".join(lines)

    @staticmethod
    def _format_time(seconds: int) -> str:
        """Format seconds into human-readable time"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
