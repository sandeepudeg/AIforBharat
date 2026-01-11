"""Report generator for database recommendations."""

from typing import Dict, List, Tuple
import pandas as pd
from src.models import Constraint, Report
from src.disqualification_engine import DisqualificationEngine
from src.scoring_engine import ScoringEngine


class ReportGenerator:
    """Generates comprehensive recommendation reports."""

    # Database characteristics for trade-off analysis
    DATABASE_CHARACTERISTICS = {
        "PostgreSQL": {
            "pros": [
                "Native support for complex joins",
                "Full ACID transactions",
                "Flexible querying (adapt to new requirements)",
                "Mature ecosystem (tools, libraries)",
                "Strong consistency guaranteed",
                "Excellent for relational data",
                "Proven at scale",
            ],
            "cons": [
                "Scaling writes requires vertical scaling or sharding",
                "Slightly higher latency (1-10ms vs. 1-5ms)",
                "Requires more operational knowledge",
                "Not ideal for time-series data",
                "Horizontal scaling is complex",
                "Cost increases with data size",
                "Requires schema management",
            ],
        },
        "DynamoDB": {
            "pros": [
                "Horizontal scaling out of the box",
                "Low latency (1-5ms typical)",
                "Fully managed service (no ops)",
                "Pay-per-request pricing option",
                "Automatic backups and replication",
                "Great for high-scale applications",
                "Excellent for key-value access patterns",
            ],
            "cons": [
                "Cannot perform joins efficiently",
                "Limited ACID support (eventual consistency)",
                "Query flexibility is limited",
                "Requires careful schema design",
                "Not suitable for complex queries",
                "Difficult to migrate from relational",
                "Learning curve for DynamoDB patterns",
            ],
        },
        "Redis": {
            "pros": [
                "Ultra-low latency (<1ms)",
                "Extremely fast in-memory performance",
                "Simple key-value operations",
                "Great for caching and sessions",
                "Low cost for small datasets",
                "Easy to set up and use",
                "Excellent for real-time data",
            ],
            "cons": [
                "Not suitable for persistent primary storage",
                "Limited to in-memory capacity",
                "Data loss on restart (without persistence)",
                "No complex query support",
                "Not designed for relational data",
                "Scaling requires clustering",
                "Limited transaction support",
            ],
        },
    }

    @staticmethod
    def generate_report(
        constraint: Constraint,
        remaining: List[str],
        disqualified: Dict[str, str],
        scores: Dict[str, float],
    ) -> Report:
        """Generate a comprehensive recommendation report.
        
        Args:
            constraint: User constraints
            remaining: List of remaining databases
            disqualified: Dict of disqualified databases and reasons
            scores: Dict of database scores
            
        Returns:
            Report object with recommendation
        """
        # Select winner (highest score)
        winner = ReportGenerator.select_winner(scores)
        
        # Generate report components
        rationale = ReportGenerator.generate_rationale(winner, constraint, disqualified)
        pros = ReportGenerator.generate_pros(winner, constraint)
        cons = ReportGenerator.generate_cons(winner, constraint)
        alternatives = ReportGenerator.generate_alternatives(winner, remaining, constraint)
        score_breakdown = ReportGenerator.generate_score_breakdown(constraint, winner)
        comparison_table = ReportGenerator.generate_comparison_table(constraint, remaining, disqualified, scores)
        
        return Report(
            winner=winner,
            score=scores.get(winner, 0.0),
            rationale=rationale,
            pros=pros,
            cons=cons,
            disqualified=disqualified,
            alternatives=alternatives,
            score_breakdown=score_breakdown,
            comparison_table=comparison_table,
        )

    @staticmethod
    def select_winner(scores: Dict[str, float]) -> str:
        """Select the database with the highest score."""
        if not scores:
            return "None"
        return max(scores, key=scores.get)

    @staticmethod
    def generate_rationale(winner: str, constraint: Constraint, disqualified: Dict[str, str]) -> str:
        """Generate rationale for the recommendation."""
        rationale_parts = []
        
        # Start with data structure
        if constraint.data_structure == "Relational":
            rationale_parts.append(f"Your data is relational with {constraint.query_complexity.lower()} queries.")
        elif constraint.data_structure == "JSON":
            rationale_parts.append(f"Your data is JSON-based with {constraint.query_complexity.lower()} queries.")
        else:
            rationale_parts.append(f"Your data is key-value based with {constraint.query_complexity.lower()} queries.")
        
        # Add consistency requirement
        if constraint.consistency_level == "Strong":
            rationale_parts.append("You require strong consistency.")
        else:
            rationale_parts.append("You can tolerate eventual consistency.")
        
        # Add scale
        rationale_parts.append(f"Your data scale is {constraint.scale_gb} GB.")
        
        # Add winner recommendation
        rationale_parts.append(f"{winner} is the clear choice for your use case.")
        
        # Add disqualification reasons
        if disqualified:
            disqualified_names = list(disqualified.keys())
            if len(disqualified_names) == 1:
                rationale_parts.append(f"{disqualified_names[0]} is disqualified because {disqualified[disqualified_names[0]].lower()}")
            else:
                reasons = " and ".join([f"{db} ({disqualified[db].lower()})" for db in disqualified_names])
                rationale_parts.append(f"{', '.join(disqualified_names)} are disqualified: {reasons}")
        
        return " ".join(rationale_parts)

    @staticmethod
    def generate_pros(winner: str, constraint: Constraint) -> List[str]:
        """Generate pros specific to the winner and constraints."""
        if winner == "None" or winner not in ReportGenerator.DATABASE_CHARACTERISTICS:
            return ["Unable to determine pros for this scenario"]
        
        all_pros = ReportGenerator.DATABASE_CHARACTERISTICS[winner]["pros"]
        
        # Filter pros based on constraints
        relevant_pros = []
        
        for pro in all_pros:
            # Add pros that match constraints
            if constraint.data_structure == "Relational" and "join" in pro.lower():
                relevant_pros.append(pro)
            elif constraint.consistency_level == "Strong" and "consistency" in pro.lower():
                relevant_pros.append(pro)
            elif constraint.scale_gb > 100 and ("scaling" in pro.lower() or "scale" in pro.lower()):
                relevant_pros.append(pro)
            elif constraint.latency_ms < 5 and "latency" in pro.lower():
                relevant_pros.append(pro)
            elif "ecosystem" in pro.lower() or "proven" in pro.lower() or "flexible" in pro.lower():
                relevant_pros.append(pro)
        
        # Ensure we have at least 3 pros
        if len(relevant_pros) < 3:
            relevant_pros = all_pros[:3]
        
        return relevant_pros[:7]  # Return up to 7 pros

    @staticmethod
    def generate_cons(winner: str, constraint: Constraint) -> List[str]:
        """Generate cons specific to the winner and constraints."""
        if winner == "None" or winner not in ReportGenerator.DATABASE_CHARACTERISTICS:
            return ["Unable to determine cons for this scenario"]
        
        all_cons = ReportGenerator.DATABASE_CHARACTERISTICS[winner]["cons"]
        
        # Filter cons based on constraints
        relevant_cons = []
        
        for con in all_cons:
            # Add cons that are relevant to constraints
            if constraint.scale_gb > 100 and "scaling" in con.lower():
                relevant_cons.append(con)
            elif constraint.latency_ms < 10 and "latency" in con.lower():
                relevant_cons.append(con)
            elif constraint.query_complexity == "Complex" and "query" in con.lower():
                relevant_cons.append(con)
            elif "cost" in con.lower() and constraint.scale_gb > 50:
                relevant_cons.append(con)
            elif "schema" in con.lower() or "knowledge" in con.lower():
                relevant_cons.append(con)
        
        # Ensure we have at least 3 cons
        if len(relevant_cons) < 3:
            relevant_cons = all_cons[:3]
        
        return relevant_cons[:7]  # Return up to 7 cons

    @staticmethod
    def generate_alternatives(winner: str, remaining: List[str], constraint: Constraint) -> Dict[str, Dict]:
        """Generate comparison of winner vs alternatives."""
        alternatives = {}
        
        for db in remaining:
            if db == winner:
                continue
            
            alternatives[db] = {
                "pros": ReportGenerator.DATABASE_CHARACTERISTICS[db]["pros"][:3],
                "cons": ReportGenerator.DATABASE_CHARACTERISTICS[db]["cons"][:3],
            }
        
        return alternatives

    @staticmethod
    def generate_score_breakdown(constraint: Constraint, winner: str) -> Dict[str, float]:
        """Generate detailed score breakdown."""
        if winner == "None" or winner not in ScoringEngine.DATABASE_PROFILES:
            return {
                "Data Structure Match": 0.0,
                "Consistency Match": 0.0,
                "Query Flexibility": 0.0,
                "Cost Score": 0.0,
                "Latency Score": 0.0,
            }
        
        # Calculate component scores
        data_score = ScoringEngine.calculate_data_structure_match(winner, constraint)
        consistency_score = ScoringEngine.calculate_consistency_match(winner, constraint)
        query_score = ScoringEngine.calculate_query_flexibility(winner, constraint)
        cost_score = ScoringEngine.calculate_cost_score(winner, constraint)
        latency_score = ScoringEngine.calculate_latency_score(winner, constraint)
        
        # Calculate weighted contributions
        breakdown = {
            "Data Structure Match": round(data_score * ScoringEngine.BASE_WEIGHTS["data_structure_match"], 3),
            "Consistency Match": round(consistency_score * ScoringEngine.BASE_WEIGHTS["consistency_match"], 3),
            "Query Flexibility": round(query_score * ScoringEngine.BASE_WEIGHTS["query_flexibility"], 3),
            "Cost Score": round(cost_score * ScoringEngine.BASE_WEIGHTS["cost_score"], 3),
            "Latency Score": round(latency_score * ScoringEngine.BASE_WEIGHTS["latency_score"], 3),
        }
        
        return breakdown

    @staticmethod
    def generate_comparison_table(
        constraint: Constraint,
        remaining: List[str],
        disqualified: Dict[str, str],
        scores: Dict[str, float],
    ) -> Dict:
        """Generate comparison table for all databases."""
        databases = remaining + list(disqualified.keys())
        
        data = {
            "Database": databases,
            "Status": ["✅ Recommended" if db == max(scores, key=scores.get) else "✅ Viable" if db in remaining else "❌ Disqualified" for db in databases],
            "Score": [scores.get(db, 0.0) for db in databases],
            "Joins": ["✅ Excellent" if db == "PostgreSQL" else "⚠️ Limited" if db == "DynamoDB" else "❌ None" for db in databases],
            "Consistency": ["✅ Strong" if db == "PostgreSQL" else "⚠️ Eventual" for db in databases],
            "Latency": ["⚠️ 1-10ms" if db == "PostgreSQL" else "✅ 1-5ms" if db == "DynamoDB" else "✅ <1ms" for db in databases],
            "Scaling": ["⚠️ Vertical" if db == "PostgreSQL" else "✅ Horizontal" if db == "DynamoDB" else "⚠️ Limited" for db in databases],
            "Cost": ["⚠️ Medium" if db == "PostgreSQL" else "✅ Low" if db == "DynamoDB" else "✅ Very Low" for db in databases],
        }
        
        # Return as dict instead of DataFrame for Pydantic compatibility
        return data
