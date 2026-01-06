import streamlit as st
import os
from environment import FileEnvironment
from agent import RecursiveAgent

# Page Config
st.set_page_config(page_title="Recursive Doc Investigator", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .log-entry { 
        font-family: 'Courier New', monospace; 
        font-size: 0.85em; 
        padding: 8px; 
        border-left: 4px solid #4CAF50; 
        margin-bottom: 6px; 
        background-color: #f8f9fa;
        border-radius: 0 5px 5px 0;
    }
    .recursion { 
        border-left: 4px solid #ff6b6b !important; 
        background-color: #fff0f0 !important; 
        font-weight: bold;
    }
    .tool { 
        border-left: 4px solid #36b9cc !important; 
        background-color: #e3f2fd !important; 
    }
    .read { 
        border-left: 4px solid #28a745 !important; 
        background-color: #f0fff4 !important; 
    }
    .search { 
        border-left: 4px solid #ffc107 !important; 
        background-color: #fff9e6 !important; 
    }
</style>
""", unsafe_allow_html=True)

st.title("🕵️ Recursive Document Investigator (RLM Implementation)")
st.markdown("### True RLM Architecture: AI Controls Navigation")
st.markdown("**Key Principle**: The AI decides what to search, what to read, and when to spawn sub-agents.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    
    # API Key Input
    api_key = st.text_input("Gemini API Key", type="password", 
                           help="Get from https://aistudio.google.com/app/apikey")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    
    st.divider()
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Document", type=["txt", "md", "log", "csv", "json"])
    
    st.divider()
    
    st.info("""
    **Sample Questions for Sherlock Holmes:**
    1. "In 'The Red-Headed League', what is Jabez Wilson's profession?"
    2. "Who does Sherlock Holmes call 'the woman' and why?"
    3. "What was in the five orange pips case?"
    """)

# --- MAIN INTERFACE ---
if uploaded_file and api_key:
    # Save uploaded file
    if not os.path.exists("data"):
        os.makedirs("data")
    
    file_path = os.path.join("data", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Initialize RLM System
    env = FileEnvironment(file_path)
    agent = RecursiveAgent(env)
    
    st.success(f"📄 Document Loaded: {uploaded_file.name} ({env.total_lines} lines)")
    
    # Query Input
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Ask a question about the document:", 
            placeholder="e.g., What is Jabez Wilson's profession in 'The Red-Headed League'?",
            key="query_input"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")
        run_button = st.button("🚀 Investigate", type="primary")
    
    if run_button and query:
        st.subheader("🔍 RLM Investigation Process")
        st.caption("Watch the AI control the investigation using tools...")
        
        # Create a container for logs
        log_container = st.container()
        
        # Callback function for UI updates
        def update_ui(message, state="neutral"):
            with log_container:
                if state == "recursion":
                    st.markdown(f"<div class='log-entry recursion'>↳ {message}</div>", 
                              unsafe_allow_html=True)
                elif state == "tool":
                    st.markdown(f"<div class='log-entry tool'>⚙️ {message}</div>", 
                              unsafe_allow_html=True)
                elif state == "read":
                    st.markdown(f"<div class='log-entry read'>📄 {message}</div>", 
                              unsafe_allow_html=True)
                elif state == "search":
                    st.markdown(f"<div class='log-entry search'>🔎 {message}</div>", 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='log-entry'>🤖 {message}</div>", 
                              unsafe_allow_html=True)
        
        # Run the RLM investigation
        with st.spinner("RLM Agent investigating..."):
            final_answer = agent.run(query, log_callback=update_ui)
        
        st.divider()
        st.subheader("✅ Investigation Result")
        st.info(final_answer)
        
        # Show explanation
        with st.expander("📊 RLM Strategy Analysis"):
            st.markdown("""
            **What just happened (RLM Style):**
            1. **AI Controlled Navigation**: The AI decided what keywords to search for
            2. **Strategic Reading**: The AI chose which sections to read based on search results
            3. **Tool-Based Investigation**: AI used functions as tools to navigate the document
            4. **Recursive Analysis**: Complex sections could be delegated to sub-agents
            
            **This is NOT RAG**: No vector similarity search. The AI actively navigates.
            """)

elif not api_key:
    st.warning("🔑 Please enter your Gemini API Key in the sidebar to start.")
else:
    st.info("📁 Please upload a document to begin investigation.")

# Footer
st.divider()
st.caption("""
**RLM vs RAG Difference**:
- **RAG**: Python finds relevant chunks → gives to AI (AI is passive)
- **RLM**: AI decides what to search → uses tools to navigate → controls investigation (AI is active)
""")
