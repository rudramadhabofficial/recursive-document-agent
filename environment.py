import os

class FileEnvironment:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.lines = f.readlines()
        self.total_lines = len(self.lines)

    def read_window(self, start_line: int, num_lines: int) -> str:
        """Reads a specific range of lines from the document."""
        # Clamp values to prevent errors
        start_line = max(0, start_line)
        end_line = min(start_line + num_lines, self.total_lines)
        
        chunk = self.lines[start_line:end_line]
        # Add line numbers to help the AI navigate
        content = "".join([f"[Line {i+start_line}] {line}" for i, line in enumerate(chunk)])
        return content

    def keyword_search(self, keyword: str) -> str:
        """Returns a list of line numbers where the keyword appears (max 50 matches)."""
        matches = []
        for i, line in enumerate(self.lines):
            if keyword.lower() in line.lower():
                matches.append(i)
                if len(matches) >= 50: # Limit to avoid context overflow
                    break
        return str(matches)

    def get_metadata(self) -> str:
        """Returns basic stats about the file."""
        return f"Filename: {os.path.basename(self.file_path)}, Total Lines: {self.total_lines}"