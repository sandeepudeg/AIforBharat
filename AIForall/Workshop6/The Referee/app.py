"""Database Referee - Streamlit Application."""

import streamlit as st
from src.constraint_parser import ConstraintParser
from src.disqualification_engine import DisqualificationEngine
from src.scoring_engine import ScoringEngine
from src.report_generator import ReportGenerator
from src.persistence import PersistenceManager
from src.models import Constraint

# Page configuration
st.set_page_config(
    page_title="Database Referee",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Default text on dark background = white */
    body, .stApp {
        color: #ffffff !important;
    }
    
    /* Green winner box - black text */
    .winner-box {
        background-color: #e6f3e6 !important;
        border: 2px solid #00aa00 !important;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        color: #000000 !important;
    }
    .winner-box * {
        color: #000000 !important;
    }
    .winner-box h2 {
        color: #000000 !important;
    }
    .winner-box h3 {
        color: #000000 !important;
    }
    
    /* Red disqualified box - black text */
    .disqualified-box {
        background-color: #ffcccc !important;
        border: 2px solid #cc0000 !important;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        color: #000000 !important;
    }
    .disqualified-box * {
        color: #000000 !important;
    }
    .disqualified-box strong {
        color: #000000 !important;
    }
    
    /* Green pros box - black text */
    .pros-box {
        background-color: #f0fff0 !important;
        border-left: 4px solid #00aa00 !important;
        padding: 15px;
        margin: 10px 0;
        color: #000000 !important;
    }
    .pros-box * {
        color: #000000 !important;
    }
    
    /* Orange cons box - black text */
    .cons-box {
        background-color: #fff0f0 !important;
        border-left: 4px solid #ff9900 !important;
        padding: 15px;
        margin: 10px 0;
        color: #000000 !important;
    }
    .cons-box * {
        color: #000000 !important;
    }
    
    /* Yellow score box - black text */
    .score-box {
        background-color: #fffacd !important;
        border: 1px solid #ccaa00 !important;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #000000 !important;
    }
    .score-box * {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("⚖️ Database Referee")
st.markdown("*Make informed database decisions based on your constraints*")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Analyzer", "History"])

if page == "Analyzer":
    st.header("Database Selection Analyzer")
    st.markdown("Answer the questions below to get a personalized database recommendation.")
    
    # Create form
    with st.form("constraint_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data & Structure")
            data_structure = st.selectbox(
                "What type of data structure do you need?",
                ["Relational", "JSON", "Key-Value"],
                help="Relational: SQL tables with joins; JSON: Document-based; Key-Value: Simple key-value pairs"
            )
            
            read_write_ratio = st.slider(
                "What percentage of operations are reads?",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                help="0% = all writes, 100% = all reads"
            )
            
            scale_gb = st.number_input(
                "What is your expected data scale (GB)?",
                min_value=0.1,
                value=10.0,
                step=1.0,
                help="Estimated total data size"
            )
        
        with col2:
            st.subheader("Requirements & Constraints")
            consistency_level = st.radio(
                "What consistency level do you need?",
                ["Strong", "Eventual"],
                help="Strong: Immediate consistency; Eventual: Delayed consistency"
            )
            
            query_complexity = st.selectbox(
                "What is your query complexity?",
                ["Simple", "Moderate", "Complex"],
                help="Simple: Key lookups; Moderate: Some filtering; Complex: Joins and aggregations"
            )
            
            latency_ms = st.number_input(
                "What is your latency requirement (ms)?",
                min_value=0.1,
                value=5.0,
                step=0.5,
                help="Maximum acceptable latency in milliseconds"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            team_expertise = st.selectbox(
                "What is your team's database expertise?",
                ["Low", "Medium", "High"],
                help="Low: Prefer managed services; High: Can handle complex setups"
            )
        
        with col4:
            requires_persistence = st.checkbox(
                "Is data persistence critical?",
                value=True,
                help="Uncheck if caching is acceptable"
            )
        
        # Submit button
        submitted = st.form_submit_button("🔍 Analyze & Get Recommendation", use_container_width=True)
    
    if submitted:
        # Parse constraints
        raw_inputs = {
            "data_structure": data_structure,
            "read_write_ratio": read_write_ratio,
            "consistency_level": consistency_level,
            "query_complexity": query_complexity,
            "scale_gb": scale_gb,
            "latency_ms": latency_ms,
            "team_expertise": team_expertise,
            "requires_persistence": requires_persistence,
        }
        
        constraint, error = ConstraintParser.parse_constraints(raw_inputs)
        
        if error:
            st.error(f"❌ Validation Error: {error.message}")
        else:
            st.success("✅ Constraints validated successfully!")
            
            # Display constraint summary
            with st.expander("📋 Your Constraints Summary"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Data Structure", constraint.data_structure)
                    st.metric("Read/Write Ratio", f"{constraint.read_write_ratio}% reads")
                    st.metric("Data Scale", f"{constraint.scale_gb} GB")
                with col2:
                    st.metric("Consistency", constraint.consistency_level)
                    st.metric("Query Complexity", constraint.query_complexity)
                    st.metric("Latency Requirement", f"{constraint.latency_ms} ms")
                with col3:
                    st.metric("Team Expertise", constraint.team_expertise)
                    st.metric("Persistence Required", "Yes" if constraint.requires_persistence else "No")
            
            # Run analysis pipeline
            st.divider()
            st.subheader("🔍 Analysis Results")
            
            # Step 1: Disqualification
            remaining, disqualified = DisqualificationEngine.disqualify(constraint)
            
            if not remaining:
                st.error("❌ No suitable databases found for your constraints.")
                st.warning("Consider relaxing some constraints:")
                for db, reason in disqualified.items():
                    st.write(f"• **{db}**: {reason}")
            else:
                # Step 2: Scoring
                scores = ScoringEngine.score_databases(constraint, remaining)
                
                # Step 3: Report Generation
                report = ReportGenerator.generate_report(constraint, remaining, disqualified, scores)
                
                # Display Winner
                st.markdown(f"""
                <div style="background-color: #e6f3e6; border: 2px solid #00aa00; border-radius: 8px; padding: 20px; margin: 10px 0; color: #0066cc;">
                    <h2 style="color: #0066cc;">🏆 Recommended Database: {report.winner}</h2>
                    <h3 style="color: #0066cc;">Score: {report.score}/10</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Display Rationale
                st.markdown("### 📝 Rationale")
                st.write(report.rationale)
                
                # Display Pros and Cons in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Advantages")
                    for pro in report.pros:
                        st.markdown(f"<div style='background-color: #f0fff0; border-left: 4px solid #00aa00; padding: 10px; margin: 5px 0; color: #0066cc;'>✓ {pro}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### ⚠️ Trade-offs")
                    for con in report.cons:
                        st.markdown(f"<div style='background-color: #fff0f0; border-left: 4px solid #ff9900; padding: 10px; margin: 5px 0; color: #0066cc;'>⚠ {con}</div>", unsafe_allow_html=True)
                
                # Display Score Breakdown
                st.divider()
                st.markdown("### 📊 Score Breakdown")
                score_col1, score_col2 = st.columns(2)
                
                with score_col1:
                    st.markdown("**Component Scores:**")
                    for component, value in report.score_breakdown.items():
                        st.write(f"• {component}: {value:.3f}")
                
                with score_col2:
                    st.markdown("**Weights Used:**")
                    for weight_name, weight_value in ScoringEngine.BASE_WEIGHTS.items():
                        st.write(f"• {weight_name.replace('_', ' ').title()}: {weight_value:.0%}")
                
                # Display Disqualified Options
                if disqualified:
                    st.divider()
                    st.markdown("### ❌ Disqualified Options")
                    for db, reason in disqualified.items():
                        st.markdown(f"<div style='background-color: #ffcccc; border: 1px solid #cc0000; border-radius: 5px; padding: 10px; margin: 5px 0; color: #0066cc;'><strong style='color: #0066cc;'>{db}</strong>: {reason}</div>", unsafe_allow_html=True)
                
                # Display Comparison Table
                st.divider()
                st.markdown("### 📋 Database Comparison")
                
                # Create comparison data
                comparison_data = report.comparison_table
                
                # Display as formatted table
                table_html = "<table style='width: 100%; border-collapse: collapse;'>"
                table_html += "<tr style='background-color: #f0f0f0;'>"
                for header in comparison_data.keys():
                    table_html += f"<th style='border: 1px solid #ddd; padding: 10px; text-align: left; color: #0066cc;'>{header}</th>"
                table_html += "</tr>"
                
                for i in range(len(comparison_data["Database"])):
                    table_html += "<tr>"
                    for key in comparison_data.keys():
                        value = comparison_data[key][i]
                        # Color code the status column
                        if key == "Status":
                            if "Recommended" in str(value):
                                bg_color = "#e6f3e6"
                            elif "Viable" in str(value):
                                bg_color = "#fffacd"
                            else:
                                bg_color = "#ffcccc"
                            table_html += f"<td style='border: 1px solid #ddd; padding: 10px; background-color: {bg_color}; color: #0066cc;'>{value}</td>"
                        else:
                            table_html += f"<td style='border: 1px solid #ddd; padding: 10px; color: #0066cc;'>{value}</td>"
                    table_html += "</tr>"
                
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
                
                # Display Alternatives
                if report.alternatives:
                    st.divider()
                    st.markdown("### 🔄 Alternative Options")
                    
                    for alt_db, alt_info in report.alternatives.items():
                        with st.expander(f"**{alt_db}** - Alternative Option"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Pros:**")
                                for pro in alt_info["pros"]:
                                    st.write(f"✓ {pro}")
                            with col2:
                                st.markdown("**Cons:**")
                                for con in alt_info["cons"]:
                                    st.write(f"⚠ {con}")
                
                # Save Configuration Section
                st.divider()
                st.markdown("### 💾 Save This Configuration")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    config_name = st.text_input(
                        "Configuration name:",
                        placeholder="e.g., 'Production Database Setup'",
                        key="save_config_name"
                    )
                with col2:
                    if st.button("Save", use_container_width=True, key="save_button"):
                        if config_name:
                            success = PersistenceManager.save_configuration(config_name, constraint)
                            if success:
                                st.success(f"✅ Configuration '{config_name}' saved!")
                            else:
                                st.error(f"❌ Failed to save configuration")
                        else:
                            st.warning("Please enter a configuration name")

elif page == "History":
    st.header("📚 Analysis History")
    
    configs = PersistenceManager.list_configurations()
    
    if not configs:
        st.info("📝 No saved configurations yet. Save one after analyzing!")
        st.markdown("""
        You can:
        - Save your constraint configurations after analysis
        - Load previous analyses
        - Compare different scenarios
        """)
    else:
        st.markdown(f"**Total Configurations**: {len(configs)}")
        st.divider()
        
        for config_name in configs:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"📋 **{config_name}**")
            
            with col2:
                if st.button("📂 Load", key=f"load_{config_name}", use_container_width=True):
                    loaded_constraint = PersistenceManager.load_configuration(config_name)
                    if loaded_constraint:
                        st.session_state.loaded_constraint = loaded_constraint
                        st.session_state.show_loaded = True
                        st.success(f"✅ Configuration '{config_name}' loaded!")
                    else:
                        st.error(f"❌ Failed to load configuration")
            
            with col3:
                if st.button("🔍 View", key=f"view_{config_name}", use_container_width=True):
                    loaded_constraint = PersistenceManager.load_configuration(config_name)
                    if loaded_constraint:
                        st.session_state.view_constraint = loaded_constraint
                        st.session_state.show_view = True
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{config_name}", use_container_width=True):
                    deleted = PersistenceManager.delete_configuration(config_name)
                    if deleted:
                        st.success(f"✅ Configuration '{config_name}' deleted!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to delete configuration")
        
        # Display loaded configuration details
        if "show_view" in st.session_state and st.session_state.show_view:
            st.divider()
            st.markdown("### 📋 Configuration Details")
            constraint = st.session_state.view_constraint
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Data Structure", constraint.data_structure)
                st.metric("Read/Write Ratio", f"{constraint.read_write_ratio}% reads")
                st.metric("Data Scale", f"{constraint.scale_gb} GB")
            with col2:
                st.metric("Consistency", constraint.consistency_level)
                st.metric("Query Complexity", constraint.query_complexity)
                st.metric("Latency Requirement", f"{constraint.latency_ms} ms")
            with col3:
                st.metric("Team Expertise", constraint.team_expertise)
                st.metric("Persistence Required", "Yes" if constraint.requires_persistence else "No")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>Database Referee v0.1.0 | Helping you make informed database decisions</p>
</div>
""", unsafe_allow_html=True)
