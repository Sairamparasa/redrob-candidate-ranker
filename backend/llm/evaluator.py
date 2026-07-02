import json
from backend.prompts.prompts import RECRUITER_EVAL_PROMPT

class RecruiterEvaluator:
    def __init__(self):
        self.prompt_template = RECRUITER_EVAL_PROMPT
        
    def evaluate_candidate(self, candidate):
        """
        Evaluate candidate and return structured criteria (Technical Match, Experience, Projects, etc.).
        Since network is disabled during ranking, we execute a rule-based mock matching
        representing the recruiter decision criteria.
        """
        # Determine technical match score
        tech_score = 0.0
        skills = [s.get("name", "").lower() for s in candidate.get("skills", [])]
        core_skills_jd = ["embeddings", "vector", "faiss", "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "python"]
        matched = [s for s in skills if any(cs in s for cs in core_skills_jd)]
        tech_score = min(len(matched) / 5.0, 1.0)
        
        # Experience match
        exp = candidate.get("years_of_experience", 0.0)
        exp_score = 0.0
        if 5.0 <= exp <= 9.0:
            exp_score = 1.0
        elif 4.0 <= exp <= 11.0:
            exp_score = 0.8
        else:
            exp_score = 0.3
            
        # Behavior score
        signals = candidate.get("signals", {})
        resp_rate = signals.get("recruiter_response_rate", 0.0)
        notice = signals.get("notice_period_days", 90)
        beh_score = (resp_rate + (1.0 if notice <= 30 else 0.5)) / 2.0
        
        evaluation = {
            "Technical Match": round(tech_score, 2),
            "Experience Match": round(exp_score, 2),
            "Projects & Domain Match": round(candidate.get("semantic_similarity", 0.5), 2),
            "Behavioral Score": round(beh_score, 2),
            "Overall Recommendation": "Recommend" if (tech_score > 0.6 and exp_score > 0.6) else "Review"
        }
        return evaluation
