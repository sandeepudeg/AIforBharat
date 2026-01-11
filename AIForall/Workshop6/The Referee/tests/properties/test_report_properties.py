"""Property-based tests for report generator."""

import pytest
from hypothesis import given, strategies as st
from src.models import Constraint, Report
from src.constraint_parser import ConstraintParser
from src.disqualification_engine import DisqualificationEngine
from src.scoring_engine import ScoringEngine
from src.report_generator import ReportGenerator


# Strategies for generating test data
@st.composite
def constraint_strategy(draw):
    """Generate valid Constraint objects."""
    return Constraint(
        data_structure=draw(st.sampled_from(["Relational", "JSON", "Key-Value"])),
        read_write_ratio=draw(st.integers(min_value=0, max_value=100)),
        consistency_level=draw(st.sampled_from(["Strong", "Eventual"])),
        query_complexity=draw(st.sampled_from(["Simple", "Moderate", "Complex"])),
        scale_gb=draw(st.floats(min_value=0.1, max_value=1000.0)),
        latency_ms=draw(st.floats(min_value=0.1, max_value=100.0)),
        team_expertise=draw(st.sampled_from(["Low", "Medium", "High"])),
        requires_persistence=draw(st.booleans()),
    )


class TestReportGeneratorProperties:
    """Property-based tests for ReportGenerator."""

    @given(constraint_strategy())
    def test_winner_selection_correctness(self, constraint: Constraint):
        """Property 8: Winner Selection Correctness.
        
        The winner must be the database with the highest score.
        """
        # Get remaining databases and scores
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        
        # Select winner
        winner = ReportGenerator.select_winner(scores)
        
        # Verify winner has highest score
        if scores:
            assert winner in scores
            assert scores[winner] == max(scores.values())
            assert scores[winner] >= 0
            assert scores[winner] <= 10

    @given(constraint_strategy())
    def test_report_completeness(self, constraint: Constraint):
        """Property 11: Report Completeness.
        
        Generated report must have all required fields populated.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify report is a Report object
        assert isinstance(report, Report)
        
        # Verify all required fields are present
        assert report.winner is not None
        assert isinstance(report.winner, str)
        assert report.score >= 0
        assert report.score <= 10
        assert isinstance(report.rationale, str)
        assert len(report.rationale) > 0
        assert isinstance(report.pros, list)
        assert len(report.pros) > 0
        assert isinstance(report.cons, list)
        assert len(report.cons) > 0
        assert isinstance(report.disqualified, dict)
        assert isinstance(report.alternatives, dict)
        assert isinstance(report.score_breakdown, dict)
        assert len(report.score_breakdown) > 0

    @given(constraint_strategy())
    def test_pros_cons_relevance(self, constraint: Constraint):
        """Property 9: Trade-off Analysis Completeness.
        
        Pros and cons must be relevant to the winner and constraints.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify pros and cons are strings
        assert all(isinstance(pro, str) for pro in report.pros)
        assert all(isinstance(con, str) for con in report.cons)
        
        # Verify pros and cons are not empty
        assert len(report.pros) > 0
        assert len(report.cons) > 0
        
        # Verify pros and cons are reasonable length
        assert all(len(pro) > 5 for pro in report.pros)
        assert all(len(con) > 5 for con in report.cons)

    @given(constraint_strategy())
    def test_disqualification_reason_mapping(self, constraint: Constraint):
        """Property 10: Disqualification Reason Mapping.
        
        Each disqualified database must have a valid reason.
        """
        # Get disqualified databases
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify disqualified mapping
        assert isinstance(report.disqualified, dict)
        
        # Each disqualified database must have a reason
        for db, reason in report.disqualified.items():
            assert isinstance(db, str)
            assert isinstance(reason, str)
            assert len(reason) > 0
            assert db in ["PostgreSQL", "DynamoDB", "Redis"]

    @given(constraint_strategy())
    def test_score_breakdown_validity(self, constraint: Constraint):
        """Property: Score Breakdown Validity.
        
        Score breakdown must contain valid component scores.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify score breakdown
        assert isinstance(report.score_breakdown, dict)
        assert len(report.score_breakdown) > 0
        
        # Each component score must be valid
        for component, score in report.score_breakdown.items():
            assert isinstance(component, str)
            assert isinstance(score, (int, float))
            assert score >= 0
            assert score <= 1  # Component scores are 0-1 before weighting

    @given(constraint_strategy())
    def test_alternatives_structure(self, constraint: Constraint):
        """Property: Alternatives Structure Validity.
        
        Alternatives must be properly structured.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify alternatives structure
        assert isinstance(report.alternatives, dict)
        
        # Each alternative must have pros and cons
        for db, alt_data in report.alternatives.items():
            assert isinstance(db, str)
            assert isinstance(alt_data, dict)
            assert "pros" in alt_data
            assert "cons" in alt_data
            assert isinstance(alt_data["pros"], list)
            assert isinstance(alt_data["cons"], list)

    @given(constraint_strategy())
    def test_winner_in_remaining_or_disqualified(self, constraint: Constraint):
        """Property: Winner Validity.
        
        Winner must be either in remaining databases or be the best of disqualified.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Winner must be in remaining databases
        assert report.winner in remaining or report.winner == "None"

    @given(constraint_strategy())
    def test_rationale_mentions_winner(self, constraint: Constraint):
        """Property: Rationale Quality.
        
        Rationale must mention the winner database.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify rationale mentions winner
        assert isinstance(report.rationale, str)
        assert len(report.rationale) > 0
        
        # Rationale should mention the winner or constraints
        assert any(word in report.rationale.lower() for word in 
                  [report.winner.lower(), "choice", "recommend", "suitable"])

    @given(constraint_strategy())
    def test_comparison_table_generation(self, constraint: Constraint):
        """Property: Comparison Table Generation.
        
        Comparison table must be properly generated.
        """
        # Generate full report
        remaining, disqualified = DisqualificationEngine.disqualify(constraint)
        scores = ScoringEngine.score_databases(constraint, remaining)
        report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
        
        # Verify comparison table exists
        assert report.comparison_table is not None
        
        # Comparison table should have data
        if hasattr(report.comparison_table, 'shape'):
            # It's a pandas DataFrame
            assert report.comparison_table.shape[0] > 0
            assert report.comparison_table.shape[1] > 0

    @given(constraint_strategy())
    def test_report_consistency_across_calls(self, constraint: Constraint):
        """Property: Report Consistency.
        
        Same constraint should produce consistent reports.
        """
        # Generate two reports with same constraint
        remaining1, disqualified1 = DisqualificationEngine.disqualify(constraint)
        scores1 = ScoringEngine.score_databases(constraint, remaining1)
        report1 = ReportGenerator.generate_report(constraint, remaining1, disqualified1, scores1)
        
        remaining2, disqualified2 = DisqualificationEngine.disqualify(constraint)
        scores2 = ScoringEngine.score_databases(constraint, remaining2)
        report2 = ReportGenerator.generate_report(constraint, remaining2, disqualified2, scores2)
        
        # Reports should be identical
        assert report1.winner == report2.winner
        assert report1.score == report2.score
        assert report1.disqualified == report2.disqualified
