import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RecursiveAgent:
    def __init__(self, env):
        self.env = env
        self.model_name = 'gemini-2.5-flash'

    def run(self, query, depth=0, max_depth=2, log_callback=None):
        """
        The main recursive loop.
        depth: Tracks how deep we are in the recursion stack.
        log_callback: Function to send UI updates.
        """
        indent = "   " * depth  # For visual hierarchy in logs
        if depth > max_depth:
            return "Max recursion depth reached. Stopping here."

        if log_callback:
            log_callback(f"{indent}🤖 [Depth {depth}] Agent Activated: {query}", state="running")

        # --- TOOL DEFINITIONS ---
        # 1. Standard Tools (File Access)
        def read_file_lines(start_line: int, num_lines: int):
            """Reads specific lines from the file to inspect content."""
            if log_callback: log_callback(f"{indent}👀 Reading lines {start_line} to {start_line + num_lines}")
            return self.env.read_window(int(start_line), int(num_lines))

        def search_for_keyword(keyword: str):
            """Finds line numbers containing a keyword."""
            if log_callback: log_callback(f"{indent}🔍 Searching for '{keyword}'")
            return self.env.keyword_search(keyword)

        # 2. The RECURSIVE Tool (The Magic)
        def delegate_subtask(sub_question: str, context_chunk: str):
            """
            Spawns a SUB-AGENT to analyze a specific text chunk. 
            Useful when you find complex data that needs focused analysis.
            """
            if log_callback: log_callback(f"{indent}🚀 [Recursion] Spawning sub-agent for: '{sub_question}'")
            
            # Create a simplified temporary agent for this chunk
            # We don't need the full file env here, just the chunk provided
            sub_prompt = f"""
            You are a sub-agent analyzer. 
            Analyze this text chunk:
            {context_chunk}
            
            Question to answer: {sub_question}
            """
            sub_model = genai.GenerativeModel('gemini-1.5-flash')
            response = sub_model.generate_content(sub_prompt)
            return response.text

        # Configure tools for Gemini
        tools_list = [read_file_lines, search_for_keyword, delegate_subtask]
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=tools_list,
            system_instruction=(
                f"You are a Recursive Document Investigator. "
                f"You cannot see the full file. You must use tools to navigate it. "
                f"File Info: {self.env.get_metadata()}. "
                f"Use 'search_for_keyword' to find locations, 'read_file_lines' to see text, "
                f"and 'delegate_subtask' if you need deep analysis of a specific section."
            )
        )

        # Start the chat session
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        try:
            response = chat.send_message(query)
            if log_callback:
                log_callback(f"{indent}✅ [Depth {depth}] Task Complete.", state="complete")
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"