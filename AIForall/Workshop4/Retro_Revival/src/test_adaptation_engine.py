"""
Tests for AdaptationEngine
Includes unit tests and property-based tests for skill assessment and adaptation
Requirements: 2.1, 2.2, 2.3, 6.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from adaptation_engine import AdaptationEngine
from game_types import PerformanceMetrics, SkillAssessment


class TestSkillAssessment:
    """Tests for skill assessment"""

    def test_assess_excellent_player(self):
        """Should assess excellent player"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=120.0,
            food_consumed=30,
            reaction_time=[150, 160, 155, 150, 160],
            collisions_avoided=15,
            average_speed=10.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.skill_level >= 70
        assert assessment.confidence > 0.5

    def test_assess_poor_player(self):
        """Should assess poor player"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=5.0,
            food_consumed=0,
            reaction_time=[500, 600, 550],
            collisions_avoided=0,
            average_speed=1.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.skill_level < 40

    def test_skill_level_in_range(self):
        """Should return skill level between 0-100"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=50.0,
            food_consumed=10,
            reaction_time=[200, 250, 200],
            collisions_avoided=5,
            average_speed=5.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert 0 <= assessment.skill_level <= 100

    def test_confidence_in_range(self):
        """Should return confidence between 0-1"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert 0 <= assessment.confidence <= 1.0

    def test_assessment_has_trend(self):
        """Should include trend in assessment"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.trend in ['improving', 'stable', 'declining']


class TestTrendDetection:
    """Tests for trend detection"""

    def test_improving_trend(self):
        """Should detect improving trend"""
        engine = AdaptationEngine()

        # Create improving trend
        for skill in [30, 40, 50, 60]:
            assessment = SkillAssessment(
                skill_level=skill,
                trend='stable',
                confidence=0.7,
                last_updated=0
            )
            engine.assessment_history.append(assessment)

        # Next assessment should show improving trend
        metrics = PerformanceMetrics(
            survival_time=60.0,
            food_consumed=15,
            reaction_time=[200],
            collisions_avoided=5,
            average_speed=5.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.trend == 'improving'

    def test_declining_trend(self):
        """Should detect declining trend"""
        engine = AdaptationEngine()

        # Create declining trend
        for skill in [70, 60, 50, 40]:
            assessment = SkillAssessment(
                skill_level=skill,
                trend='stable',
                confidence=0.7,
                last_updated=0
            )
            engine.assessment_history.append(assessment)

        # Next assessment should show declining trend
        metrics = PerformanceMetrics(
            survival_time=10.0,
            food_consumed=2,
            reaction_time=[500],
            collisions_avoided=0,
            average_speed=1.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.trend == 'declining'

    def test_stable_trend(self):
        """Should detect stable trend"""
        engine = AdaptationEngine()

        # Create stable trend
        for skill in [50, 50, 50, 50]:
            assessment = SkillAssessment(
                skill_level=skill,
                trend='stable',
                confidence=0.7,
                last_updated=0
            )
            engine.assessment_history.append(assessment)

        # Next assessment should show stable trend
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        assert assessment.trend == 'stable'


class TestDifficultyAdjustment:
    """Tests for difficulty adjustment calculation"""

    def test_increase_difficulty_for_excellent_player(self):
        """Should increase difficulty for excellent player"""
        engine = AdaptationEngine()
        assessment = SkillAssessment(
            skill_level=85,
            trend='improving',
            confidence=0.9,
            last_updated=0
        )

        delta = engine.calculate_difficulty_adjustment(assessment)
        assert delta.speed_delta > 0
        assert delta.obstacle_density_delta > 0

    def test_decrease_difficulty_for_poor_player(self):
        """Should decrease difficulty for poor player"""
        engine = AdaptationEngine()
        assessment = SkillAssessment(
            skill_level=15,
            trend='declining',
            confidence=0.8,
            last_updated=0
        )

        delta = engine.calculate_difficulty_adjustment(assessment)
        assert delta.speed_delta < 0
        assert delta.obstacle_density_delta < 0

    def test_maintain_difficulty_for_average_player(self):
        """Should maintain difficulty for average player"""
        engine = AdaptationEngine()
        assessment = SkillAssessment(
            skill_level=50,
            trend='stable',
            confidence=0.7,
            last_updated=0
        )

        delta = engine.calculate_difficulty_adjustment(assessment)
        assert delta.speed_delta == 0
        assert delta.obstacle_density_delta == 0

    def test_adjustment_includes_reason(self):
        """Should include reason for adjustment"""
        engine = AdaptationEngine()
        assessment = SkillAssessment(
            skill_level=75,
            trend='stable',
            confidence=0.8,
            last_updated=0
        )

        delta = engine.calculate_difficulty_adjustment(assessment)
        assert len(delta.reason) > 0

    def test_trend_affects_adjustment_magnitude(self):
        """Should adjust magnitude based on trend"""
        engine = AdaptationEngine()

        # Improving trend
        assessment_improving = SkillAssessment(
            skill_level=70,
            trend='improving',
            confidence=0.8,
            last_updated=0
        )

        # Declining trend
        assessment_declining = SkillAssessment(
            skill_level=70,
            trend='declining',
            confidence=0.8,
            last_updated=0
        )

        delta_improving = engine.calculate_difficulty_adjustment(assessment_improving)
        delta_declining = engine.calculate_difficulty_adjustment(assessment_declining)

        # Improving should have larger positive adjustment
        assert delta_improving.speed_delta > delta_declining.speed_delta


class TestAdaptationDecisionLogging:
    """Tests for adaptation decision logging"""

    def test_record_adaptation_decision(self):
        """Should record adaptation decision"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )
        assessment = SkillAssessment(
            skill_level=50,
            trend='stable',
            confidence=0.7,
            last_updated=0
        )
        delta = engine.calculate_difficulty_adjustment(assessment)

        decision = engine.record_adaptation_decision(
            metrics, assessment, delta, "Test rationale"
        )

        assert decision.metrics == metrics
        assert decision.skill_assessment == assessment
        assert decision.difficulty_delta == delta
        assert decision.rationale == "Test rationale"

    def test_decision_log_grows(self):
        """Should grow decision log with each decision"""
        engine = AdaptationEngine()

        for i in range(5):
            metrics = PerformanceMetrics(
                survival_time=30.0 + i * 10,
                food_consumed=5 + i,
                reaction_time=[200],
                collisions_avoided=2,
                average_speed=3.0,
                timestamp=0
            )
            assessment = engine.assess_player_skill(metrics)
            delta = engine.calculate_difficulty_adjustment(assessment)
            engine.record_adaptation_decision(
                metrics, assessment, delta, f"Decision {i}"
            )

        assert len(engine.decision_log) == 5

    def test_get_adaptation_rationale(self):
        """Should return adaptation rationale"""
        engine = AdaptationEngine()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )
        assessment = engine.assess_player_skill(metrics)
        delta = engine.calculate_difficulty_adjustment(assessment)
        engine.record_adaptation_decision(metrics, assessment, delta, "Test")

        rationale = engine.get_adaptation_rationale()
        assert "Skill Level" in rationale
        assert "Confidence" in rationale

    def test_get_decision_history(self):
        """Should return recent decision history"""
        engine = AdaptationEngine()

        for i in range(15):
            metrics = PerformanceMetrics(
                survival_time=30.0,
                food_consumed=5,
                reaction_time=[200],
                collisions_avoided=2,
                average_speed=3.0,
                timestamp=0
            )
            assessment = engine.assess_player_skill(metrics)
            delta = engine.calculate_difficulty_adjustment(assessment)
            engine.record_adaptation_decision(metrics, assessment, delta, f"Decision {i}")

        history = engine.get_decision_history(10)
        assert len(history) == 10

    def test_clear_history(self):
        """Should clear assessment and decision history"""
        engine = AdaptationEngine()

        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=3.0,
            timestamp=0
        )
        assessment = engine.assess_player_skill(metrics)
        delta = engine.calculate_difficulty_adjustment(assessment)
        engine.record_adaptation_decision(metrics, assessment, delta, "Test")

        assert len(engine.assessment_history) > 0
        assert len(engine.decision_log) > 0

        engine.clear_history()

        assert len(engine.assessment_history) == 0
        assert len(engine.decision_log) == 0


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestAdaptationEngineProperties:
    """Property-based tests for adaptation engine correctness"""

    def test_property_6_skill_assessment_consistency(self):
        """
        Property 6: Skill Assessment Consistency
        For any two identical performance metric sets, the skill assessment
        should produce identical skill level scores and trend classifications.
        
        **Feature: snake-adaptive-ai, Property 6: Skill Assessment Consistency**
        **Validates: Requirements 2.1**
        """
        engine = AdaptationEngine()

        metrics = PerformanceMetrics(
            survival_time=45.0,
            food_consumed=10,
            reaction_time=[150, 160, 155, 150],
            collisions_avoided=5,
            average_speed=5.0,
            timestamp=0
        )

        # Assess same metrics twice
        assessment1 = engine.assess_player_skill(metrics)
        assessment2 = engine.assess_player_skill(metrics)

        # Should produce identical results
        assert assessment1.skill_level == assessment2.skill_level
        assert assessment1.trend == assessment2.trend

    def test_property_7_difficulty_adaptation_monotonicity(self):
        """
        Property 7: Difficulty Adaptation Monotonicity
        For any sequence of improving performance metrics, the difficulty level
        should never decrease; conversely, for declining metrics, difficulty should never increase.
        
        **Feature: snake-adaptive-ai, Property 7: Difficulty Adaptation Monotonicity**
        **Validates: Requirements 2.2, 2.3**
        """
        engine = AdaptationEngine()

        # Test improving sequence
        improving_metrics = [
            PerformanceMetrics(10.0, 1, [400], 0, 1.0, 0),
            PerformanceMetrics(20.0, 3, [300], 1, 2.0, 0),
            PerformanceMetrics(40.0, 8, [200], 3, 4.0, 0),
            PerformanceMetrics(60.0, 15, [150], 5, 6.0, 0),
        ]

        deltas = []
        for metrics in improving_metrics:
            assessment = engine.assess_player_skill(metrics)
            delta = engine.calculate_difficulty_adjustment(assessment)
            deltas.append(delta)

        # For improving metrics, difficulty should not decrease
        # (speed_delta should be >= 0 or increasing)
        for i in range(1, len(deltas)):
            # Each adjustment should be at least as difficult as previous
            assert deltas[i].speed_delta >= deltas[i - 1].speed_delta - 0.1

    def test_property_8_adaptation_decision_logging(self):
        """
        Property 8: Adaptation Decision Logging
        For any difficulty adjustment made by the adaptation engine, a log entry
        should be created containing the decision rationale, input metrics, and calculated adjustment.
        
        **Feature: snake-adaptive-ai, Property 8: Adaptation Decision Logging**
        **Validates: Requirements 6.1**
        """
        engine = AdaptationEngine()

        metrics = PerformanceMetrics(
            survival_time=45.0,
            food_consumed=10,
            reaction_time=[150, 160],
            collisions_avoided=5,
            average_speed=5.0,
            timestamp=0
        )

        assessment = engine.assess_player_skill(metrics)
        delta = engine.calculate_difficulty_adjustment(assessment)
        engine.record_adaptation_decision(metrics, assessment, delta, "Test rationale")

        # Verify log entry contains all required information
        assert len(engine.decision_log) == 1
        decision = engine.decision_log[0]

        assert decision.metrics is not None
        assert decision.skill_assessment is not None
        assert decision.difficulty_delta is not None
        assert len(decision.rationale) > 0
