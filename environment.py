import os

class BaseEnvironment:
    """Base class for environments - can be file or string based"""
    def __init__(self):
        self.lines = []
        self.total_lines = 0
    
    def read_window(self, start_line: int, num_lines: int) -> str:
        """Reads a specific range of lines."""
        start_line = max(0, start_line)
        end_line = min(start_line + num_lines, self.total_lines)
        
        chunk = self.lines[start_line:end_line]
        content = "".join([f"[Line {i+start_line}] {line}" for i, line in enumerate(chunk)])
        return content
    
    def keyword_search(self, keyword: str) -> str:
        """Finds line numbers containing a keyword."""
        matches = []
        for i, line in enumerate(self.lines):
            if keyword.lower() in line.lower():
                matches.append(i)
                if len(matches) >= 50:
                    break
        return str(matches)
    
    def get_metadata(self) -> str:
        return f"Base Environment, Total Lines: {self.total_lines}"

class FileEnvironment(BaseEnvironment):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.lines = f.readlines()
        self.total_lines = len(self.lines)
    
    def get_metadata(self) -> str:
        return f"Filename: {os.path.basename(self.file_path)}, Total Lines: {self.total_lines}"

class StringEnvironment(BaseEnvironment):
    """Environment for a string chunk - used by sub-agents"""
    def __init__(self, text: str):
        super().__init__()
        self.lines = text.splitlines(keepends=True)
        self.total_lines = len(self.lines)
    
    def get_metadata(self) -> str:
        return f"String Environment, Total Lines: {self.total_lines}"
