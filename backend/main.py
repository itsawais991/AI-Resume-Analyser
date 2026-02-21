"""
AI Resume Analyzer - FastAPI Backend
Main entry point with file upload endpoint and health check.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf_parser import extract_text_from_pdf, get_pdf_metadata
from ats_graph import analyze_resume

app = FastAPI(
    title="AI Resume Analyzer",
    description="ATS Score Checker using RAG + LangChain + LangGraph",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    version: str


class AnalysisResponse(BaseModel):
    success: bool
    data: dict
    message: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Upload a PDF resume and receive an ATS analysis report.
    
    - Accepts PDF files only (max 10MB)
    - Returns overall score, category breakdowns, and improvement suggestions
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    # Read file
    file_bytes = await file.read()

    # Validate file size (max 10MB)
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit.",
        )

    # Validate API key
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Please set it in the .env file.",
        )

    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file_bytes)

        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the PDF. Ensure it's a text-based PDF, not a scanned image.",
            )

        # Get PDF metadata
        metadata = get_pdf_metadata(file_bytes)

        # Run ATS analysis via LangGraph
        report = await analyze_resume(resume_text, metadata)

        return AnalysisResponse(
            success=True,
            data=report,
            message="Resume analysis completed successfully.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
