import json
from backend.ingestion.parser import parse_candidate
from backend.utils.helpers import is_honeypot
from backend.ranking.scorer import get_title_score, get_experience_score, get_skill_score, get_behavioral_score, get_location_multiplier
from backend.config import WEIGHT_TITLE, WEIGHT_SKILL, WEIGHT_EXPERIENCE, WEIGHT_BEHAVIOR

def retrieve_top_candidates(candidates_path, limit=1500):
    """
    Scans the candidates pool, performs honeypot checks, applies fast heuristics,
    and returns the top candidate matches for semantic evaluation.
    """
    candidates_pool = []
    skipped_honeypots = 0
    total_count = 0
    
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total_count += 1
            raw = json.loads(line)
            parsed = parse_candidate(raw)
            
            # Honeypot Check
            if is_honeypot(parsed):
                skipped_honeypots += 1
                continue
                
            # Score Components
            title_score = get_title_score(parsed["current_title"])
            if title_score == 0.0:  # Disqualified title
                continue
                
            exp_score = get_experience_score(parsed["years_of_experience"], parsed["career_history"])
            skill_score = get_skill_score(parsed["skills"], parsed["signals"])
            beh_score = get_behavioral_score(parsed["signals"])
            loc_mult = get_location_multiplier(
                parsed["location"], 
                parsed["country"], 
                parsed["signals"].get("willing_to_relocate", False)
            )
            
            # Combine heuristic score
            heuristic_score = (
                title_score * WEIGHT_TITLE +
                skill_score * WEIGHT_SKILL +
                exp_score * WEIGHT_EXPERIENCE +
                beh_score * WEIGHT_BEHAVIOR
            ) * loc_mult
            
            parsed["heuristic_score"] = heuristic_score
            candidates_pool.append(parsed)
            
    print(f"Total processed in candidates pool: {total_count}")
    print(f"Honeypots skipped: {skipped_honeypots}")
    print(f"Candidates passing initial heuristic filter: {len(candidates_pool)}")
    
    # Sort and return top candidates
    candidates_pool.sort(key=lambda x: x["heuristic_score"], reverse=True)
    top_k = min(limit, len(candidates_pool))
    return candidates_pool[:top_k]
