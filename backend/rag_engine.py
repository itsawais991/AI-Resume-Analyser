"""
Simple RAG Engine Module (Fallback Version)
Manages retrieval from knowledge documents using simple file reading.
Used as a fallback for Python 3.14 environment where ChromaDB is incompatible.
"""

import os
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

def retrieve_relevant_knowledge(query: str, k: int = 5) -> str:
    """
    Retrieve all ATS knowledge (simple version for stable deployment).
    Since the knowledge base is small, we return the content of all files.
    """
    all_content = []
    
    if not KNOWLEDGE_DIR.exists():
        return "No ATS knowledge documents found."
        
    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_content.append(f.read())
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return "\n\n---\n\n".join(all_content)
