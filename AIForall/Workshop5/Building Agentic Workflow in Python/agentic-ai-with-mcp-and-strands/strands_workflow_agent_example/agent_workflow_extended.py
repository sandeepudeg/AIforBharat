import streamlit as st
import asyncio
import os
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request
from dotenv import load_dotenv

# 1. Configuration
load_dotenv()
st.set_page_config(page_title="AI Research Assistant", page_icon="🔬", layout="wide")

# 2. Robust Extraction Helper (Prevents attribute errors)
def extract_text(result):
    """Safely extracts text regardless of whether result is an object or dict."""
    try:
        # Check for .message (Object) or ['message'] (Dict)
        msg = result.message if hasattr(result, 'message') else result.get('message')
        # Check for .content or ['content']
        content = msg.content if hasattr(msg, 'content') else msg.get('content')
        # Get text from first block
        block = content[0]
        return block.text if hasattr(block, 'text') else block.get('text', str(block))
    except Exception:
        return str(result)

# 3. Agent Factory (Cached for speed)
@st.cache_resource
def get_agents():
    # Using Nova-Lite for fast parallel execution
    model = BedrockModel(model_id="us.amazon.nova-lite-v1:0", temperature=0.1)
    
    researcher = Agent(
        model=model,
        tools=[http_request],
        system_prompt="You are a Researcher. Gather facts with source URLs."
    )
    
    writer = Agent(
        model=model,
        system_prompt="You are a Writer. Create a professional Markdown report from research data."
    )
    
    return researcher, writer

# 4. Multi-Agent Workflow Logic
async def execute_workflow(query):
    researcher, writer = get_agents()
    
    # --- Parallel Research Step ---
    with st.status("🌐 Stage 1: Parallel Web Research...", expanded=True) as status:
        st.write("Searching multiple sources simultaneously...")
        
        # Branching: Fetch two different perspectives at the same time
        task1 = researcher.invoke_async(f"Provide 3 historical facts about: {query}")
        task2 = researcher.invoke_async(f"Provide 3 recent data points/news about: {query}")
        
        results = await asyncio.gather(task1, task2)
        
        combined_data = f"DATASET A:\n{extract_text(results[0])}\n\nDATASET B:\n{extract_text(results[1])}"
        status.update(label="✅ Research Gathered", state="complete", expanded=False)

    # --- Synthesis Step ---
    with st.status("✍️ Stage 2: Drafting Final Report...", expanded=True) as status:
        report_result = await writer.invoke_async(f"Write a report using this data:\n\n{combined_data}")
        final_text = extract_text(report_result)
        status.update(label="✅ Report Drafted", state="complete", expanded=False)
        
    return final_text

# 5. UI Layout
st.title("🔬 Pro Research Assistant")
st.caption("Using Strands & Amazon Bedrock for Agentic Workflow")

# Session History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display Chat
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input Logic
if prompt := st.chat_input("What would you like me to research?"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Run async workflow
            response_text = asyncio.run(execute_workflow(prompt))
            
            st.markdown(response_text)
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            
            # --- ADDED: DOWNLOAD FEATURE ---
            st.divider()
            st.download_button(
                label="📥 Download Research Report",
                data=response_text,
                file_name=f"research_report_{prompt[:15].replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error occurred: {e}")
            if "ExpiredTokenException" in str(e):
                st.warning("Refresh your AWS session: run 'aws sso login'.")

# Sidebar for Debug/Status
with st.sidebar:
    st.header("Agent Status")
    st.write("🟢 Researcher: Ready")
    st.write("🟢 Writer: Ready")
    if st.button("Clear Session"):
        st.session_state.chat_history = []
        st.rerun()