import streamlit as st
import os
from environment import FileEnvironment
from agent import RecursiveAgent

# Page Config
st.set_page_config(page_title="Recursive Doc Investigator", layout="wide")

# Custom CSS for the logs
st.markdown("""
<style>
    .log-entry { font-family: monospace; font-size: 0.9em; padding: 5px; border-left: 3px solid #4CAF50; margin-bottom: 5px; background-color: #f0f2f6; }
    .recursion { border-left: 3px solid #ff4b4b !important; background-color: #fff5f5 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🕵️ Recursive Document Investigator (RDI)")
st.markdown("### MIT RLM-Inspired Agentic Workflow")
st.markdown("This tool processes massive files by **programmatically navigating** them rather than loading everything at once.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    
    # API Key Input
    api_key = st.text_input("Gemini API Key", type="password", help="Get from aistudio.google.com")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    
    st.divider()
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Target File", type=["txt", "log", "py", "md"])

    # Helper to generate dummy data if user has none
    if st.button("Generate Dummy 'Massive' Log File"):
        if not os.path.exists("data"):
            os.makedirs("data")
        with open("data/massive_log.txt", "w") as f:
            f.write("System Boot Sequence Initiated...\n")
            for i in range(10000):
                f.write(f"LOG_ENTRY_{i}: Routine check. System status normal. Memory usage stable.\n")
            # Hide a secret needle in the haystack
            f.write("LOG_ENTRY_10001: CRITICAL ERROR: DATABASE TIMEOUT on TUESDAY due to LOCKED TABLE 'Users'.\n")
            for i in range(10002, 20000):
                 f.write(f"LOG_ENTRY_{i}: Recovery sequence. System status normal.\n")
        st.success("Generated 'data/massive_log.txt' (20,000 lines) with a hidden error!")

# --- MAIN LOGIC ---
if uploaded_file and api_key:
    # Save the uploaded file locally
    if not os.path.exists("data"):
        os.makedirs("data")
    
    file_path = os.path.join("data", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Initialize Environment
    env = FileEnvironment(file_path)
    agent = RecursiveAgent(env)
    
    st.success(f"File Loaded: {uploaded_file.name} ({env.total_lines} lines)")

    # User Query
    query = st.text_input("Ask a question about the file:", placeholder="e.g., Why did the system crash?")

    if st.button("Investigate"):
        st.subheader("Agent Thought Process")
        log_container = st.container()

        # Callback function to print live updates to UI
        def update_ui(message, state="neutral"):
            with log_container:
                style = "recursion" if "Recursion" in message else "log-entry"
                st.markdown(f"<div class='{style}'>{message}</div>", unsafe_allow_html=True)

        with st.spinner("Agent is recursively investigating..."):
            final_answer = agent.run(query, log_callback=update_ui)
        
        st.divider()
        st.subheader("Final Answer")
        st.info(final_answer)

elif not api_key:
    st.warning("👈 Please enter your Gemini API Key in the sidebar to start.")