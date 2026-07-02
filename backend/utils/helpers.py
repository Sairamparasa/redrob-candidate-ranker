import datetime

def parse_date(date_str):
    """
    Safely parse date string to datetime object.
    """
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def is_honeypot(candidate):
    """
    Detects honeypots and anomalous profiles.
    Returns True if the profile is identified as a honeypot.
    """
    # Check 1: Expert or Advanced skills with 0 duration
    for s in candidate.get("skills", []):
        proficiency = s.get("proficiency", "").lower()
        duration = s.get("duration_months", 0)
        if proficiency in ["advanced", "expert"] and duration == 0:
            return True

    # Check 2: Impossible job calendar dates
    now_date = datetime.datetime(2026, 7, 2)
    for j in candidate.get("career_history", []):
        start_date = parse_date(j.get("start_date"))
        if not start_date:
            continue
            
        if j.get("is_current") or not j.get("end_date"):
            max_months = ((now_date - start_date).days / 30.4) + 2.0
        else:
            end_date = parse_date(j.get("end_date"))
            if not end_date:
                continue
            max_months = ((end_date - start_date).days / 30.4) + 2.0
            
        if j.get("duration_months", 0) > max_months:
            return True

    # Check 3: Sum of job durations vs profile years of experience
    y = candidate.get("years_of_experience", 0.0)
    sum_dur = sum(j.get("duration_months", 0) for j in candidate.get("career_history", []))
    if y > 1.0:
        if sum_dur < (y * 12) * 0.1:
            return True
        if sum_dur > (y * 12) + 24:
            return True

    # Check 4: Signup date after last active date or in the future
    signals = candidate.get("signals", {})
    signup_date = parse_date(signals.get("signup_date"))
    active_date = parse_date(signals.get("last_active_date"))
    if signup_date and active_date:
        if signup_date > active_date or signup_date > now_date or active_date > now_date:
            return True

    return False
