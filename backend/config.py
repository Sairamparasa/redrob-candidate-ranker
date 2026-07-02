import os

# Base paths
WORKSPACE_DIR = r"c:\Users\saira\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"

# Embedding model path (local)
EMBEDDINGS_MODEL_DIR = os.path.join(WORKSPACE_DIR, "backend", "embeddings", "all-MiniLM-L6-v2")

# Candidate Pool Path
CANDIDATES_PATH = os.path.join(WORKSPACE_DIR, "candidates.jsonl")

# Scoring Parameters
TOP_K_RETRIEVAL = 1500  # Number of candidates to evaluate semantically

# Hybrid Scoring Weights (must sum to 1.0)
WEIGHT_TITLE = 0.35       # Matches core ML/AI vs software/backend roles
WEIGHT_SEMANTIC = 0.25    # Semantic similarity of profile/summary against JD
WEIGHT_SKILL = 0.20       # Direct core ML/AI skill match
WEIGHT_EXPERIENCE = 0.10  # Duration match (focusing on 5-9 year target)
WEIGHT_BEHAVIOR = 0.10    # Multiplier on platform activity and response rates
