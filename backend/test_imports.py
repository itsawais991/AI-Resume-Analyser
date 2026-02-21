import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

print("Testing imports...")
try:
    from pdf_parser import extract_text_from_pdf, get_pdf_metadata
    print("pdf_parser imported ok")
except Exception as e:
    print(f"pdf_parser import failed: {e}")

try:
    from rag_engine import retrieve_relevant_knowledge
    print("rag_engine imported ok")
except Exception as e:
    print(f"rag_engine import failed: {e}")

try:
    from ats_graph import analyze_resume
    print("ats_graph imported ok")
except Exception as e:
    print(f"ats_graph import failed: {e}")

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
