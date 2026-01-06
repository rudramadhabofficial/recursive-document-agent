import os
import time
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RecursiveAgent:
    def __init__(self, env):
        self.env = env
        self.model_name = 'gemini-2.5-flash'  # Using a stable model
    
    def run(self, query, depth=0, max_depth=2, log_callback=None):
        """
        Main recursive RLM loop.
        The AI controls the investigation using tools.
        """
        indent = "   " * depth
        if depth > max_depth:
            return "Max recursion depth reached. Stopping here."
        
        if log_callback:
            log_callback(f"{indent}🤖 [Depth {depth}] Agent Activated: {query}", state="running")
        
        # Define the TOOLS as FunctionDeclaration objects for Gemini
        tools = [
            FunctionDeclaration(
                name="read_file_lines",
                description="Read specific lines from the document to inspect content",
                parameters={
                    "type": "object",
                    "properties": {
                        "start_line": {"type": "integer", "description": "Line number to start reading from (0-indexed)"},
                        "num_lines": {"type": "integer", "description": "Number of lines to read"}
                    },
                    "required": ["start_line", "num_lines"]
                }
            ),
            FunctionDeclaration(
                name="search_for_keyword",
                description="Find line numbers where a keyword appears",
                parameters={
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Keyword to search for"}
                    },
                    "required": ["keyword"]
                }
            ),
            FunctionDeclaration(
                name="delegate_subtask",
                description="Spawn a sub-agent to analyze a specific text chunk in detail. Use this when you need focused analysis on a complex section.",
                parameters={
                    "type": "object",
                    "properties": {
                        "sub_question": {"type": "string", "description": "The specific question for the sub-agent to answer"},
                        "context_chunk": {"type": "string", "description": "The text chunk the sub-agent should analyze"}
                    },
                    "required": ["sub_question", "context_chunk"]
                }
            )
        ]
        
        # Create the model with tools
        model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=tools,
            system_instruction=(
                f"You are a Recursive Document Investigator using RLM principles. "
                f"You CANNOT see the entire file at once. You must use tools strategically. "
                f"File Info: {self.env.get_metadata()}. "
                f"STRATEGY: First, search for keywords to locate relevant sections. "
                f"Then, read those sections. If a section is complex, delegate it to a sub-agent. "
                f"Remember: You are in control. You decide what to search, what to read, and when to spawn sub-agents."
            )
        )
        
        # Start chat with manual function calling (AI decides when to use tools)
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        try:
            # Initial message with query
            response = chat.send_message(query)
            
            # Process the response and handle function calls
            while response.candidates[0].content.parts[0].function_call:
                # Get the function call
                func_call = response.candidates[0].content.parts[0].function_call
                func_name = func_call.name
                args = func_call.args
                
                if log_callback:
                    log_callback(f"{indent}🔧 Tool Call: {func_name}({args})", state="tool")
                
                # Execute the tool
                if func_name == "read_file_lines":
                    result = self.env.read_window(args["start_line"], args["num_lines"])
                    if log_callback:
                        log_callback(f"{indent}📖 Read lines {args['start_line']}-{args['start_line']+args['num_lines']}", state="read")
                
                elif func_name == "search_for_keyword":
                    result = self.env.keyword_search(args["keyword"])
                    if log_callback:
                        log_callback(f"{indent}🔍 Searched for '{args['keyword']}' - Found at lines: {result}", state="search")
                
                elif func_name == "delegate_subtask":
                    # Create a string-based environment for the sub-agent
                    from environment import StringEnvironment
                    sub_env = StringEnvironment(args["context_chunk"])
                    sub_agent = RecursiveAgent(sub_env)
                    
                    if log_callback:
                        log_callback(f"{indent}🚀 Spawning sub-agent for: '{args['sub_question']}'", state="recursion")
                    
                    # Recursively call the sub-agent
                    time.sleep(2)  # Rate limiting
                    result = sub_agent.run(
                        args["sub_question"], 
                        depth=depth+1, 
                        max_depth=2, 
                        log_callback=log_callback
                    )
                
                else:
                    result = f"Unknown function: {func_name}"
                
                # Send the result back to the AI
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=func_name,
                                response={"result": result}
                            )
                        )]
                    )
                )
            
            # Final answer
            final_answer = response.text
            if log_callback:
                log_callback(f"{indent}✅ [Depth {depth}] Task Complete.", state="complete")
            
            return final_answer
            
        except Exception as e:
            return f"Error: {str(e)}"
