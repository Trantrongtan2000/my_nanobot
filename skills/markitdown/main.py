#!/usr/bin/env python3
"""
markitdown skill - Convert Office documents to Markdown
Usage: python3 main.py <file_path>
"""

import sys
import os

def convert_to_markdown(file_path):
    """Convert Office document to Markdown using markitdown."""
    try:
        from markitdown import MarkItDown
    except ImportError:
        return "Error: markitdown package not installed. Run: pip install markitdown"
    
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"
    
    try:
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        return f"Error converting file: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    markdown = convert_to_markdown(file_path)
    print(markdown)