"""
Pause Menu Component
Displays pause functionality with performance summary showing recent metrics and skill assessment
Requirements: 3.3
"""

from typing import Optional
from game_types import PerformanceMetrics, SkillAssessment


class PauseMenu:
    """Manages pause state and displays performance summary"""

    def __init__(self):
        """Initialize the pause menu"""
        self.is_paused = False
        self.current_metrics: Optional[PerformanceMetrics] = None
        self.current_skill_assessment: Optional[SkillAssessment] = None

    def pause(self) -> None:
        """Pause the game"""
        self.is_paused = True

    def resume(self) -> None:
        """Resume the game"""
        self.is_paused = False

    def toggle_pause(self) -> bool:
        """Toggle pause state and return new state"""
        self.is_paused = not self.is_paused
        return self.is_paused

    def is_game_paused(self) -> bool:
        """Check if game is paused"""
        return self.is_paused

    def set_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Set the current performance metrics to display"""
        self.current_metrics = metrics

    def set_skill_assessment(self, assessment: SkillAssessment) -> None:
        """Set the current skill assessment to display"""
        self.current_skill_assessment = assessment

    def get_performance_summary(self) -> str:
        """Get formatted performance summary for display"""
        if not self.current_metrics:
            return "No performance data available"

        lines = []
        lines.append("=== PERFORMANCE SUMMARY ===")
        lines.append("")

        # Survival time
        survival_minutes = int(self.current_metrics.survival_time // 60)
        survival_seconds = int(self.current_metrics.survival_time % 60)
        lines.append(f"Survival Time: {survival_minutes}m {survival_seconds}s")

        # Food consumed
        lines.append(f"Food Consumed: {self.current_metrics.food_consumed}")

        # Reaction time
        if self.current_metrics.reaction_time:
            avg_reaction = sum(self.current_metrics.reaction_time) / len(self.current_metrics.reaction_time)
            lines.append(f"Average Reaction Time: {avg_reaction:.0f}ms")

        # Collisions avoided
        lines.append(f"Collisions Avoided: {self.current_metrics.collisions_avoided}")

        # Average speed
        lines.append(f"Average Speed: {self.current_metrics.average_speed:.1f}")

        return "\n".join(lines)

    def get_skill_assessment_summary(self) -> str:
        """Get formatted skill assessment summary for display"""
        if not self.current_skill_assessment:
            return "No skill assessment available"

        lines = []
        lines.append("")
        lines.append("=== SKILL ASSESSMENT ===")
        lines.append("")

        # Skill level
        lines.append(f"Skill Level: {self.current_skill_assessment.skill_level}/100")

        # Trend
        trend_display = self._format_trend(self.current_skill_assessment.trend)
        lines.append(f"Trend: {trend_display}")

        # Confidence
        confidence_percent = int(self.current_skill_assessment.confidence * 100)
        lines.append(f"Confidence: {confidence_percent}%")

        return "\n".join(lines)

    def _format_trend(self, trend: str) -> str:
        """Format trend for display"""
        if trend == 'improving':
            return "📈 Improving"
        elif trend == 'declining':
            return "📉 Declining"
        else:
            return "➡️ Stable"

    def get_full_pause_display(self) -> str:
        """Get complete pause menu display with all information"""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════╗")
        lines.append("║           GAME PAUSED                  ║")
        lines.append("╚════════════════════════════════════════╝")
        lines.append("")

        # Add performance summary
        lines.append(self.get_performance_summary())

        # Add skill assessment
        lines.append(self.get_skill_assessment_summary())

        lines.append("")
        lines.append("Press SPACE to resume or Q to quit")
        lines.append("")

        return "\n".join(lines)

    def get_pause_header(self) -> str:
        """Get just the pause header"""
        return "GAME PAUSED - Press SPACE to resume"

    def get_metrics_display(self) -> str:
        """Get just the metrics display"""
        return self.get_performance_summary()

    def get_assessment_display(self) -> str:
        """Get just the assessment display"""
        return self.get_skill_assessment_summary()

    def has_metrics(self) -> bool:
        """Check if metrics are available"""
        return self.current_metrics is not None

    def has_assessment(self) -> bool:
        """Check if skill assessment is available"""
        return self.current_skill_assessment is not None

    def clear_data(self) -> None:
        """Clear stored metrics and assessment"""
        self.current_metrics = None
        self.current_skill_assessment = None
