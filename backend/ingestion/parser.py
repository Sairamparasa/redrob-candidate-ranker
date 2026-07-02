import json
import os
from backend.config import WORKSPACE_DIR

def load_jd_requirements():
    jd_path = os.path.join(WORKSPACE_DIR, "backend", "ingestion", "jd_requirements.json")
    with open(jd_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_candidate(raw):
    """
    Parses and extracts key features from raw candidate data.
    """
    cid = raw.get("candidate_id")
    profile = raw.get("profile", {})
    skills = raw.get("skills", [])
    career = raw.get("career_history", [])
    education = raw.get("education", [])
    signals = raw.get("redrob_signals", {})
    
    # Text summary for embeddings
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    
    # Aggregate career descriptions
    career_texts = []
    for job in career:
        comp = job.get("company", "")
        title = job.get("title", "")
        desc = job.get("description", "")
        career_texts.append(f"{title} at {comp}: {desc}")
    career_full_text = " | ".join(career_texts)
    
    # Skill names list
    skill_names = [s.get("name", "") for s in skills]
    skills_text = ", ".join(skill_names)
    
    # Build text representation for semantic embeddings
    embed_text = f"Title: {profile.get('current_title', '')} | Headline: {headline} | Summary: {summary} | Skills: {skills_text} | Work History: {career_full_text}"
    
    return {
        "candidate_id": cid,
        "name": profile.get("anonymized_name", ""),
        "current_title": profile.get("current_title", ""),
        "current_company": profile.get("current_company", ""),
        "years_of_experience": profile.get("years_of_experience", 0.0),
        "location": profile.get("location", ""),
        "country": profile.get("country", ""),
        "skills": skills,
        "skill_names": skill_names,
        "career_history": career,
        "education": education,
        "signals": signals,
        "embed_text": embed_text
    }
