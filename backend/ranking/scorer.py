import datetime
from backend.utils.helpers import is_honeypot
from backend.ingestion.parser import load_jd_requirements

# Load static JD requirements once
JD = load_jd_requirements()

def get_title_score(title):
    """
    Evaluates current job title alignment with the JD.
    """
    title_lower = title.lower()
    
    # 1. Check disqualified titles
    for dt in JD["disqualified_titles"]:
        if dt in title_lower:
            return 0.0
            
    # 2. Check core ML/AI keywords
    ml_keywords = ["ml", "ai", "machine learning", "data scientist", "nlp", "computer vision", "deep learning", "applied ml", "ai specialist", "research engineer"]
    for k in ml_keywords:
        # Use boundary check or substring check
        if k in title_lower:
            return 1.0
            
    # 3. Check adjacent software engineering roles
    swe_keywords = ["software engineer", "backend engineer", "data engineer", "cloud engineer", "devops engineer", "systems engineer", "full stack developer", "java developer", "developer", "engineer", "architect", "tech lead", "technical lead", "staff engineer"]
    for k in swe_keywords:
        if k in title_lower:
            return 0.6
            
    return 0.1

def get_experience_score(years_exp, career_history):
    """
    Evaluates experience duration fit. Target is 5-9 years.
    Also penalizes profiles that have ONLY consulting company history.
    """
    # Experience years score
    if 5.0 <= years_exp <= 9.0:
        exp_score = 1.0
    elif 4.0 <= years_exp < 5.0 or 9.0 < years_exp <= 11.0:
        exp_score = 0.8
    elif 3.0 <= years_exp < 4.0 or 11.0 < years_exp <= 13.0:
        exp_score = 0.5
    else:
        exp_score = 0.1
        
    # Consulting company check
    companies = [j.get("company", "").lower() for j in career_history if j.get("company")]
    if companies:
        only_consulting = True
        for comp in companies:
            is_c = False
            for cc in JD["disqualified_companies"]:
                if cc in comp:
                    is_c = True
                    break
            if not is_c:
                only_consulting = False
                break
        if only_consulting:
            exp_score *= 0.2  # Apply a heavy consulting penalty as per JD

    return exp_score

def get_skill_score(candidate_skills, signals):
    """
    Calculates direct skill match score.
    Uses proficiency, endorsements, and platform assessment scores.
    """
    if not candidate_skills:
        return 0.0
        
    matched_score = 0.0
    total_weights = 0.0
    
    # Redrob skill assessments
    assessments = signals.get("skill_assessment_scores", {})
    
    for s in candidate_skills:
        name = s.get("name", "").lower()
        proficiency = s.get("proficiency", "beginner").lower()
        endorsements = s.get("endorsements", 0)
        duration = s.get("duration_months", 0)
        
        # Check if matches core or preferred skills
        is_core = False
        is_pref = False
        
        for cs in JD["core_skills"]:
            if cs in name or name in cs:
                is_core = True
                break
                
        if not is_core:
            for ps in JD["preferred_skills"]:
                if ps in name or name in ps:
                    is_pref = True
                    break
                    
        if not (is_core or is_pref):
            continue
            
        # Skill weight based on type
        skill_weight = 1.0 if is_core else 0.5
        
        # Proficiency multiplier
        prof_mult = 0.25
        if proficiency == "intermediate":
            prof_mult = 0.60
        elif proficiency == "advanced":
            prof_mult = 0.85
        elif proficiency == "expert":
            prof_mult = 1.0
            
        # Endorsements and duration trust factor
        trust_factor = 0.6
        trust_factor += min(duration / 24.0, 1.0) * 0.2
        trust_factor += min(endorsements / 50.0, 1.0) * 0.2
        
        # Assessment score boost
        assessment_boost = 1.0
        for skill_name, score in assessments.items():
            if skill_name.lower() in name or name in skill_name.lower():
                assessment_boost = 1.0 + (score / 100.0) * 0.3
                break
                
        skill_val = skill_weight * prof_mult * trust_factor * assessment_boost
        matched_score += skill_val
        total_weights += skill_weight
        
    if total_weights == 0:
        return 0.0
        
    # Normalize and cap at 1.0
    return min(matched_score / 3.0, 1.0)

def get_behavioral_score(signals):
    """
    Evaluates availability, activity, and response signals.
    """
    # 1. Recruiter Response Rate
    response_rate = signals.get("recruiter_response_rate", 0.0)
    # A base factor of 0.2 plus response rate
    rr_score = 0.2 + 0.8 * response_rate
    
    # 2. Activity Recency
    active_str = signals.get("last_active_date", "2020-01-01")
    try:
        active_date = datetime.datetime.strptime(active_str, "%Y-%m-%d")
        now_date = datetime.datetime(2026, 7, 2)
        days_inactive = (now_date - active_date).days
        if days_inactive <= 30:
            recency_score = 1.0
        elif days_inactive <= 90:
            recency_score = 0.8
        elif days_inactive <= 180:
            recency_score = 0.5
        else:
            recency_score = 0.1
    except ValueError:
        recency_score = 0.1
        
    # 3. Notice Period
    notice_days = signals.get("notice_period_days", 90)
    if notice_days <= 30:
        notice_score = 1.0
    elif notice_days <= 60:
        notice_score = 0.8
    elif notice_days <= 90:
        notice_score = 0.5
    else:
        notice_score = 0.2
        
    # 4. Open to Work and Github boosts
    open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.7
    
    github_score = signals.get("github_activity_score", -1)
    github_mult = 1.0
    if github_score > 0:
        github_mult = 1.0 + (github_score / 100.0) * 0.1
        
    beh_score = (rr_score + recency_score + notice_score + open_to_work) / 4.0
    return min(beh_score * github_mult, 1.0)

def get_location_multiplier(location, country, willing_to_relocate):
    """
    Penalizes candidates outside of India who won't relocate.
    Favors Noida/Pune.
    """
    loc_lower = location.lower()
    country_lower = country.lower()
    
    # Check if candidate is located outside India
    is_india = "india" in country_lower or any(l in loc_lower for l in ["pune", "noida", "bangalore", "bengaluru", "hyderabad", "mumbai", "delhi", "gurgaon"])
    
    if not is_india:
        if not willing_to_relocate:
            return 0.1  # Major disqualifier if not willing to relocate
        return 0.4
        
    # Noida / Pune priority
    if "noida" in loc_lower or "pune" in loc_lower:
        return 1.0
    # Other India Hubs
    other_hubs = ["bangalore", "bengaluru", "hyderabad", "mumbai", "delhi", "gurgaon", "ncr"]
    if any(h in loc_lower for h in other_hubs):
        return 0.95
        
    return 0.8
