import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands_multi_agent_example.computer_science_assistant import computer_science_assistant
from strands_multi_agent_example.english_assistant import english_assistant
from strands_multi_agent_example.language_assistant import language_assistant
from strands_multi_agent_example.math_assistant import math_assistant
from strands_multi_agent_example.no_expertise import general_assistant
from strands_tools import memory, use_agent, mem0_memory, use_llm
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["BYPASS_TOOL_CONSENT"] = "true"

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")

TEACHER_SYSTEM_PROMPT = """
You are TeachAssist, a sophisticated educational orchestrator designed to coordinate educational support across multiple subjects. Your role is to:

1. Analyze incoming student queries and determine the most appropriate specialized agent to handle them:
   - Math Agent: For mathematical calculations, problems, and concepts
   - English Agent: For writing, grammar, literature, and composition
   - Language Agent: For translation and language-related queries
   - Computer Science Agent: For programming, algorithms, data structures, and code execution
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify student queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query involves calculations/numbers → Math Agent
   - If query involves writing/literature/grammar → English Agent
   - If query involves translation → Language Agent
   - If query involves programming/coding/algorithms/computer science → Computer Science Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

TEACHER_KEYWORDS = ["math", "calculate", "solve", "equation", "write", "essay", "grammar", "translate", "code", "program", "algorithm", "python", "java", "javascript"]

def determine_action(query):
    """Determine if query should go to teacher agent or knowledge base agent."""
    query_lower = query.lower()
    for keyword in TEACHER_KEYWORDS:
        if keyword in query_lower:
            return "teacher"
    return "knowledge_base"

def run_kb_agent(query):
    """Process query with knowledge base agent."""
    bedrock_model = BedrockModel(
        model_id='us.amazon.nova-pro-v1:0',
        temperature=0.1,
    )
    agent = Agent(
        model=bedrock_model,
        tools=[memory, use_agent]
    )
    
    try:
        result = agent.tool.memory(
            action="retrieve", 
            query=query,
            min_score=float(os.getenv("MIN_SCORE", "0.00001")),
            max_results=int(os.getenv("MAX_RESULTS", "9"))
        )
        return str(result)
    except Exception as e:
        return f"Error retrieving from knowledge base: {str(e)}"

def run_memory_agent(query, user_id="default_user"):
    """Process query with memory agent (Open Search backend)."""
    bedrock_model = BedrockModel(
        model_id='us.amazon.nova-pro-v1:0',
        temperature=0.1,
    )
    agent = Agent(
        model=bedrock_model,
        system_prompt="You remember user preferences and context.",
        tools=[mem0_memory, use_llm]
    )
    
    try:
        result = agent(query, invocation_state={"user_id": user_id})
        return str(result)
    except Exception as e:
        return f"Error with memory agent: {str(e)}"

def get_teacher_agent(model_id, selected_tools):
    bedrock_model = BedrockModel(
        model_id=model_id,
        temperature=0.3,
    )
    return Agent(
        model=bedrock_model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        tools=selected_tools,
    )

st.title("📁 Teacher's Assistant & Knowledge Base Chatbot")
st.write("Ask questions in any subject area or retrieve information from the knowledge base.")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Model selection
    model_options = [
        "us.amazon.nova-pro-v1:0",
        "us.amazon.nova-lite-v1:0",
        "us.amazon.nova-micro-v1:0",
        "anthropic.claude-3-5-haiku-20241022-v1:0",
        "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "anthropic.claude-sonnet-4-20250514-v1:0"
    ]
    selected_model = st.selectbox("Select Model:", model_options)
    
    # Backend selection
    backend_options = ["Bedrock Knowledge Base"]
    if OPENSEARCH_HOST:
        backend_options.append("Open Search Memory")
    selected_backend = st.selectbox("Select Backend:", backend_options)
    
    # Teacher agent tools selection
    st.subheader("Teacher Agent Tools")
    all_tools = {
        "Math Assistant": math_assistant,
        "English Assistant": english_assistant,
        "Language Assistant": language_assistant,
        "Computer Science Assistant": computer_science_assistant,
        "General Assistant": general_assistant
    }
    
    selected_tool_names = []
    for tool_name in all_tools.keys():
        if st.checkbox(tool_name, value=True):
            selected_tool_names.append(tool_name)
    
    selected_tools = [all_tools[name] for name in selected_tool_names] if selected_tool_names else [general_assistant]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    action = determine_action(user_input)
    
    with st.chat_message("assistant"):
        if action == "teacher":
            teacher_agent = get_teacher_agent(selected_model, selected_tools)
            response = str(teacher_agent(user_input))
        elif selected_backend == "Open Search Memory":
            response = run_memory_agent(user_input)
        else:
            response = run_kb_agent(user_input)
        
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
