"""
ATS Analysis Graph Module
LangGraph workflow for multi-step resume ATS analysis.
Nodes: parse → retrieve → analyze (formatting, keywords, experience, skills) → report
"""

import os
import json
import re
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from rag_engine import retrieve_relevant_knowledge


# ─── State Schema ───────────────────────────────────────────────────────────

class ATSState(TypedDict):
    """State passed through the LangGraph workflow."""
    resume_text: str
    resume_metadata: dict
    parsed_sections: dict
    ats_knowledge: str
    formatting_score: dict
    keyword_score: dict
    experience_score: dict
    skills_score: dict
    final_report: dict


# ─── LLM Helper ─────────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )


def parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try to find JSON in code blocks first
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object or array in the text
        for pattern in [r'\{.*\}', r'\[.*\]']:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
    
    return {"error": "Failed to parse LLM response", "raw": text[:500]}


# ─── Node Functions ─────────────────────────────────────────────────────────

def parse_resume(state: ATSState) -> dict:
    """Node 1: Parse resume text into structured sections."""
    llm = get_llm()

    prompt = f"""Analyze this resume text and extract the following sections. 
Return a JSON object with these keys (use empty string if section not found):

{{
    "contact_info": "extracted contact information",
    "professional_summary": "professional summary or objective",
    "work_experience": "all work experience entries",
    "education": "education section",
    "skills": "skills section",
    "certifications": "certifications if any",
    "projects": "projects if any",
    "other_sections": "any other notable sections",
    "detected_job_field": "the likely industry/field based on content",
    "estimated_experience_years": "estimated years of professional experience as a number"
}}

Resume text:
{state["resume_text"]}
"""
    response = llm.invoke(prompt)
    parsed = parse_json_response(response.content)

    return {"parsed_sections": parsed}


def retrieve_ats_knowledge(state: ATSState) -> dict:
    """Node 2: Retrieve relevant ATS best-practice knowledge via RAG (Fallback version)."""
    # Build a query from the resume's detected field and content
    parsed = state.get("parsed_sections", {})
    field = parsed.get("detected_job_field", "general")
    skills = parsed.get("skills", "")

    query = f"ATS best practices for {field} resume with skills: {skills[:200]}"
    knowledge = retrieve_relevant_knowledge(query, k=6)

    return {"ats_knowledge": knowledge}


def analyze_formatting(state: ATSState) -> dict:
    """Node 3: Analyze resume formatting and structure."""
    llm = get_llm()
    knowledge = state.get("ats_knowledge", "")
    parsed = state.get("parsed_sections", {})
    metadata = state.get("resume_metadata", {})

    prompt = f"""You are an expert ATS resume analyst. Analyze this resume's formatting and structure.

ATS Best Practices Knowledge:
{knowledge}

Resume Metadata:
- Pages: {metadata.get('page_count', 'Unknown')}
- File size: {metadata.get('file_size_kb', 'Unknown')} KB

Resume Sections Found:
- Contact Info: {"Yes" if parsed.get("contact_info") else "No"}
- Professional Summary: {"Yes" if parsed.get("professional_summary") else "No"}
- Work Experience: {"Yes" if parsed.get("work_experience") else "No"}
- Education: {"Yes" if parsed.get("education") else "No"}
- Skills: {"Yes" if parsed.get("skills") else "No"}
- Certifications: {"Yes" if parsed.get("certifications") else "No"}

Resume Text (first 2000 chars):
{state["resume_text"][:2000]}

Return a JSON object:
{{
    "score": <number 0-100>,
    "strengths": ["list of formatting strengths"],
    "weaknesses": ["list of formatting issues"],
    "suggestions": ["specific improvement suggestions"],
    "details": {{
        "has_contact_info": <bool>,
        "has_summary": <bool>,
        "has_experience": <bool>,
        "has_education": <bool>,
        "has_skills": <bool>,
        "proper_section_order": <bool>,
        "appropriate_length": <bool>,
        "clean_formatting": <bool>
    }}
}}
"""
    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"formatting_score": result}


def analyze_keywords(state: ATSState) -> dict:
    """Node 4: Analyze keyword optimization."""
    llm = get_llm()
    knowledge = state.get("ats_knowledge", "")
    parsed = state.get("parsed_sections", {})

    prompt = f"""You are an expert ATS keyword analyst. Analyze this resume's keyword optimization.

ATS Keyword Best Practices:
{knowledge}

Detected Job Field: {parsed.get("detected_job_field", "Unknown")}

Resume Skills Section:
{parsed.get("skills", "No skills section found")}

Resume Work Experience:
{parsed.get("work_experience", "No experience section found")}

Professional Summary:
{parsed.get("professional_summary", "No summary found")}

Return a JSON object:
{{
    "score": <number 0-100>,
    "strengths": ["keyword strengths found"],
    "weaknesses": ["keyword optimization issues"],
    "suggestions": ["specific keyword improvements"],
    "details": {{
        "industry_keywords_found": ["list of relevant industry keywords found"],
        "missing_common_keywords": ["important keywords that are missing"],
        "action_verbs_used": ["strong action verbs found"],
        "has_quantified_achievements": <bool>,
        "keyword_density_assessment": "low/appropriate/high"
    }}
}}
"""
    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"keyword_score": result}


def analyze_experience(state: ATSState) -> dict:
    """Node 5: Analyze work experience quality."""
    llm = get_llm()
    parsed = state.get("parsed_sections", {})

    prompt = f"""You are an expert ATS resume analyst. Analyze the quality of work experience in this resume.

Work Experience:
{parsed.get("work_experience", "No experience section found")}

Estimated Years: {parsed.get("estimated_experience_years", "Unknown")}
Detected Field: {parsed.get("detected_job_field", "Unknown")}

Return a JSON object:
{{
    "score": <number 0-100>,
    "strengths": ["experience section strengths"],
    "weaknesses": ["experience section issues"],
    "suggestions": ["specific experience improvement suggestions"],
    "details": {{
        "has_quantified_results": <bool>,
        "uses_action_verbs": <bool>,
        "shows_progression": <bool>,
        "relevant_to_field": <bool>,
        "bullet_point_quality": "poor/fair/good/excellent",
        "achievement_vs_duty_ratio": "mostly duties/balanced/mostly achievements"
    }}
}}
"""
    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"experience_score": result}


def analyze_skills(state: ATSState) -> dict:
    """Node 6: Analyze skills section."""
    llm = get_llm()
    parsed = state.get("parsed_sections", {})

    prompt = f"""You are an expert ATS resume analyst. Analyze the skills section of this resume.

Skills Section:
{parsed.get("skills", "No skills section found")}

Detected Job Field: {parsed.get("detected_job_field", "Unknown")}
Certifications: {parsed.get("certifications", "None found")}

Return a JSON object:
{{
    "score": <number 0-100>,
    "strengths": ["skills section strengths"],
    "weaknesses": ["skills section issues"],
    "suggestions": ["specific skills improvement suggestions"],
    "details": {{
        "technical_skills_count": <number>,
        "soft_skills_count": <number>,
        "has_skill_categories": <bool>,
        "skills_relevant_to_field": <bool>,
        "has_certifications": <bool>,
        "missing_key_skills": ["important skills missing for the field"]
    }}
}}
"""
    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"skills_score": result}


def generate_final_report(state: ATSState) -> dict:
    """Node 7: Generate the final comprehensive ATS report."""
    llm = get_llm()

    formatting = state.get("formatting_score", {})
    keywords = state.get("keyword_score", {})
    experience = state.get("experience_score", {})
    skills = state.get("skills_score", {})
    parsed = state.get("parsed_sections", {})

    # Calculate weighted overall score
    fmt_score = formatting.get("score", 50)
    kw_score = keywords.get("score", 50)
    exp_score = experience.get("score", 50)
    sk_score = skills.get("score", 50)

    # Weights: Keywords 35%, Experience 25%, Skills 20%, Formatting 20%
    overall_score = round(
        kw_score * 0.35 + exp_score * 0.25 + sk_score * 0.20 + fmt_score * 0.20
    )

    prompt = f"""You are an expert ATS resume consultant. Generate a final summary analysis.

Overall ATS Score: {overall_score}/100

Category Scores:
- Formatting & Structure: {fmt_score}/100
- Keyword Optimization: {kw_score}/100
- Experience Quality: {exp_score}/100
- Skills Presentation: {sk_score}/100

Detected field: {parsed.get("detected_job_field", "Unknown")}

All strengths found:
- Formatting: {formatting.get("strengths", [])}
- Keywords: {keywords.get("strengths", [])}
- Experience: {experience.get("strengths", [])}
- Skills: {skills.get("strengths", [])}

All weaknesses found:
- Formatting: {formatting.get("weaknesses", [])}
- Keywords: {keywords.get("weaknesses", [])}
- Experience: {experience.get("weaknesses", [])}
- Skills: {skills.get("weaknesses", [])}

Generate a JSON response with:
{{
    "summary": "2-3 sentence overall assessment of the resume",
    "top_improvements": [
        {{
            "priority": "high/medium/low",
            "category": "formatting/keywords/experience/skills",
            "title": "short title of the improvement",
            "description": "detailed actionable suggestion"
        }}
    ],
    "ats_compatibility": "poor/fair/good/excellent",
    "estimated_pass_rate": "percentage chance this resume passes ATS screening"
}}

Provide exactly 5-8 improvement items, ordered by priority (high first).
"""
    response = llm.invoke(prompt)
    summary_data = parse_json_response(response.content)

    final_report = {
        "overall_score": overall_score,
        "category_scores": {
            "formatting": {
                "score": fmt_score,
                "label": "Formatting & Structure",
                "weight": "20%",
                "strengths": formatting.get("strengths", []),
                "weaknesses": formatting.get("weaknesses", []),
                "suggestions": formatting.get("suggestions", []),
                "details": formatting.get("details", {}),
            },
            "keywords": {
                "score": kw_score,
                "label": "Keyword Optimization",
                "weight": "35%",
                "strengths": keywords.get("strengths", []),
                "weaknesses": keywords.get("weaknesses", []),
                "suggestions": keywords.get("suggestions", []),
                "details": keywords.get("details", {}),
            },
            "experience": {
                "score": exp_score,
                "label": "Experience Quality",
                "weight": "25%",
                "strengths": experience.get("strengths", []),
                "weaknesses": experience.get("weaknesses", []),
                "suggestions": experience.get("suggestions", []),
                "details": experience.get("details", {}),
            },
            "skills": {
                "score": sk_score,
                "label": "Skills Presentation",
                "weight": "20%",
                "strengths": skills.get("strengths", []),
                "weaknesses": skills.get("weaknesses", []),
                "suggestions": skills.get("suggestions", []),
                "details": skills.get("details", {}),
            },
        },
        "summary": summary_data.get("summary", "Analysis complete."),
        "top_improvements": summary_data.get("top_improvements", []),
        "ats_compatibility": summary_data.get("ats_compatibility", "fair"),
        "estimated_pass_rate": summary_data.get("estimated_pass_rate", "N/A"),
        "detected_field": parsed.get("detected_job_field", "Unknown"),
    }

    return {"final_report": final_report}


# ─── Build the LangGraph ────────────────────────────────────────────────────

def build_ats_graph():
    """
    Build and compile the LangGraph for ATS analysis.
    
    Workflow:
    parse_resume → retrieve_ats_knowledge → [analyze_formatting, analyze_keywords,
    analyze_experience, analyze_skills] → generate_final_report
    """
    workflow = StateGraph(ATSState)

    # Add nodes
    workflow.add_node("parse_resume", parse_resume)
    workflow.add_node("retrieve_ats_knowledge", retrieve_ats_knowledge)
    workflow.add_node("analyze_formatting", analyze_formatting)
    workflow.add_node("analyze_keywords", analyze_keywords)
    workflow.add_node("analyze_experience", analyze_experience)
    workflow.add_node("analyze_skills", analyze_skills)
    workflow.add_node("generate_final_report", generate_final_report)

    # Define edges — sequential flow 
    workflow.set_entry_point("parse_resume")
    workflow.add_edge("parse_resume", "retrieve_ats_knowledge")
    workflow.add_edge("retrieve_ats_knowledge", "analyze_formatting")
    workflow.add_edge("analyze_formatting", "analyze_keywords")
    workflow.add_edge("analyze_keywords", "analyze_experience")
    workflow.add_edge("analyze_experience", "analyze_skills")
    workflow.add_edge("analyze_skills", "generate_final_report")
    workflow.add_edge("generate_final_report", END)

    return workflow.compile()


# ─── Public API ──────────────────────────────────────────────────────────────

async def analyze_resume(resume_text: str, resume_metadata: dict) -> dict:
    """
    Run the full ATS analysis pipeline on a resume.
    
    Args:
        resume_text: Extracted text from the PDF resume.
        resume_metadata: Metadata about the PDF file.
        
    Returns:
        Final analysis report dictionary.
    """
    graph = build_ats_graph()

    initial_state = {
        "resume_text": resume_text,
        "resume_metadata": resume_metadata,
        "parsed_sections": {},
        "ats_knowledge": "",
        "formatting_score": {},
        "keyword_score": {},
        "experience_score": {},
        "skills_score": {},
        "final_report": {},
    }

    # Run the graph
    result = await graph.ainvoke(initial_state)
    return result["final_report"]
