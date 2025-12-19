"""
Skill assessment and difficulty adaptation engine
Analyzes player performance and adjusts game difficulty
Requirements: 2.1, 2.2, 2.3, 6.1
"""

import time
from typing import List, Optional
from game_types import (
    PerformanceMetrics,
    SkillAssessment,
    DifficultyDelta,
    AdaptationDecision,
)


class AdaptationEngine:
    """Manages skill assessment and difficulty adaptation"""

    # Skill assessment thresholds
    SKILL_THRESHOLD_EXCELLENT = 80
    SKILL_THRESHOLD_GOOD = 60
    SKILL_THRESHOLD_AVERAGE = 40
    SKILL_THRESHOLD_POOR = 20

    def __init__(self):
        """Initialize adaptation engine"""
        self.assessment_history: List[SkillAssessment] = []
        self.decision_log: List[AdaptationDecision] = []

    def assess_player_skill(self, metrics: PerformanceMetrics) -> SkillAssessment:
        """
        Assess player skill level based on performance metrics
        Returns skill level 0-100 with trend and confidence
        """
        # Calculate skill components
        survival_score = self._calculate_survival_score(metrics.survival_time)
        food_score = self._calculate_food_score(metrics.food_consumed, metrics.survival_time)
        reaction_score = self._calculate_reaction_score(metrics.reaction_time)
        collision_score = self._calculate_collision_score(metrics.collisions_avoided)

        # Weighted average of components
        skill_level = int(
            (survival_score * 0.3 +
             food_score * 0.3 +
             reaction_score * 0.2 +
             collision_score * 0.2)
        )

        # Clamp to 0-100
        skill_level = max(0, min(100, skill_level))

        # Determine trend
        trend = self._determine_trend()

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(metrics)

        assessment = SkillAssessment(
            skill_level=skill_level,
            trend=trend,
            confidence=confidence,
            last_updated=int(time.time() * 1000)
        )

        self.assessment_history.append(assessment)
        return assessment

    def _calculate_survival_score(self, survival_time: float) -> float:
        """Calculate skill score based on survival time"""
        # Score increases with survival time
        # 30 seconds = 50 points, 60 seconds = 80 points, 120+ seconds = 100 points
        if survival_time < 10:
            return survival_time * 2
        elif survival_time < 30:
            return 20 + (survival_time - 10) * 1.5
        elif survival_time < 60:
            return 50 + (survival_time - 30) * 1.0
        else:
            return min(100, 80 + (survival_time - 60) * 0.3)

    def _calculate_food_score(self, food_consumed: int, survival_time: float) -> float:
        """Calculate skill score based on food consumption"""
        if survival_time == 0:
            return 0.0

        # Calculate food per minute
        minutes = survival_time / 60.0
        food_per_minute = food_consumed / minutes if minutes > 0 else 0

        # Score based on consumption rate
        # 1 food/min = 20 points, 5 food/min = 60 points, 10+ food/min = 100 points
        if food_per_minute < 1:
            return food_per_minute * 20
        elif food_per_minute < 5:
            return 20 + (food_per_minute - 1) * 10
        elif food_per_minute < 10:
            return 60 + (food_per_minute - 5) * 8
        else:
            return min(100, 100 + (food_per_minute - 10) * 2)

    def _calculate_reaction_score(self, reaction_times: List[int]) -> float:
        """Calculate skill score based on reaction time"""
        if not reaction_times:
            return 50.0  # Neutral score if no data

        avg_reaction = sum(reaction_times) / len(reaction_times)

        # Score based on average reaction time (in ms)
        # 200ms = 100 points, 300ms = 70 points, 500ms = 30 points
        if avg_reaction <= 200:
            return 100.0
        elif avg_reaction <= 300:
            return 100 - (avg_reaction - 200) * 0.3
        elif avg_reaction <= 500:
            return 70 - (avg_reaction - 300) * 0.2
        else:
            return max(0, 30 - (avg_reaction - 500) * 0.05)

    def _calculate_collision_score(self, collisions_avoided: int) -> float:
        """Calculate skill score based on collision avoidance"""
        # More collisions avoided = higher score
        # 0 avoided = 20 points, 5 avoided = 60 points, 10+ avoided = 100 points
        if collisions_avoided < 5:
            return 20 + collisions_avoided * 8
        elif collisions_avoided < 10:
            return 60 + (collisions_avoided - 5) * 8
        else:
            return min(100, 100 + (collisions_avoided - 10) * 2)

    def _determine_trend(self) -> str:
        """Determine skill trend from assessment history"""
        if len(self.assessment_history) < 2:
            return 'stable'

        # Compare last 3 assessments
        recent = self.assessment_history[-3:]
        if len(recent) < 2:
            return 'stable'

        # Calculate average of first half vs second half
        mid = len(recent) // 2
        first_half_avg = sum(a.skill_level for a in recent[:mid]) / len(recent[:mid])
        second_half_avg = sum(a.skill_level for a in recent[mid:]) / len(recent[mid:])

        improvement = second_half_avg - first_half_avg

        if improvement > 5:
            return 'improving'
        elif improvement < -5:
            return 'declining'
        else:
            return 'stable'

    def _calculate_confidence(self, metrics: PerformanceMetrics) -> float:
        """Calculate confidence in skill assessment"""
        confidence = 0.5  # Base confidence

        # More reaction time data = higher confidence
        if len(metrics.reaction_time) > 10:
            confidence += 0.2
        elif len(metrics.reaction_time) > 5:
            confidence += 0.1

        # Longer survival time = higher confidence
        if metrics.survival_time > 60:
            confidence += 0.2
        elif metrics.survival_time > 30:
            confidence += 0.1

        # More food consumed = higher confidence
        if metrics.food_consumed > 10:
            confidence += 0.1

        return min(1.0, confidence)

    def calculate_difficulty_adjustment(
        self, assessment: SkillAssessment
    ) -> DifficultyDelta:
        """
        Calculate difficulty adjustment based on skill assessment
        Returns delta for speed, obstacle density, and food spawn rate
        """
        skill_level = assessment.skill_level
        trend = assessment.trend

        # Base adjustments based on skill level
        if skill_level >= self.SKILL_THRESHOLD_EXCELLENT:
            speed_delta = 1.0
            obstacle_delta = 1.0
            food_delta = 0.2
            reason = "Excellent performance - increasing difficulty"
        elif skill_level >= self.SKILL_THRESHOLD_GOOD:
            speed_delta = 0.5
            obstacle_delta = 0.5
            food_delta = 0.1
            reason = "Good performance - slightly increasing difficulty"
        elif skill_level >= self.SKILL_THRESHOLD_AVERAGE:
            speed_delta = 0.0
            obstacle_delta = 0.0
            food_delta = 0.0
            reason = "Average performance - maintaining difficulty"
        elif skill_level >= self.SKILL_THRESHOLD_POOR:
            speed_delta = -0.5
            obstacle_delta = -0.5
            food_delta = -0.1
            reason = "Below average performance - decreasing difficulty"
        else:
            speed_delta = -1.0
            obstacle_delta = -1.0
            food_delta = -0.2
            reason = "Poor performance - significantly decreasing difficulty"

        # Adjust based on trend
        if trend == 'improving':
            speed_delta *= 1.2
            obstacle_delta *= 1.2
        elif trend == 'declining':
            speed_delta *= 0.8
            obstacle_delta *= 0.8

        return DifficultyDelta(
            speed_delta=speed_delta,
            obstacle_density_delta=obstacle_delta,
            food_spawn_rate_delta=food_delta,
            reason=reason
        )

    def record_adaptation_decision(
        self,
        metrics: PerformanceMetrics,
        assessment: SkillAssessment,
        delta: DifficultyDelta,
        rationale: str
    ) -> AdaptationDecision:
        """Record an adaptation decision for logging and analysis"""
        decision = AdaptationDecision(
            timestamp=int(time.time() * 1000),
            metrics=metrics,
            skill_assessment=assessment,
            difficulty_delta=delta,
            rationale=rationale
        )

        self.decision_log.append(decision)
        return decision

    def get_adaptation_rationale(self) -> str:
        """Get explanation of recent adaptation decisions"""
        if not self.decision_log:
            return "No adaptation decisions made yet"

        recent_decision = self.decision_log[-1]
        assessment = recent_decision.skill_assessment

        rationale = f"Skill Level: {assessment.skill_level}/100 ({assessment.trend})\n"
        rationale += f"Confidence: {assessment.confidence:.1%}\n"
        rationale += f"Adjustment: {recent_decision.difficulty_delta.reason}"

        return rationale

    def get_decision_history(self, count: int = 10) -> List[AdaptationDecision]:
        """Get recent adaptation decisions"""
        return self.decision_log[-count:]

    def clear_history(self) -> None:
        """Clear assessment and decision history"""
        self.assessment_history = []
        self.decision_log = []
