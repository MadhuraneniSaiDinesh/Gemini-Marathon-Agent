# tools.py
import os

def create_file(filename: str, content: str):
    """
    Creates a new file with the specified content.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"SUCCESS: Created file '{filename}'."
    except Exception as e:
        return f"ERROR: Could not create file. Reason: {e}"

# This list tells Gemini what tools it is allowed to use
my_tools = [create_file]