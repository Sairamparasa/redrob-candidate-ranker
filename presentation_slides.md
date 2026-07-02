# Hackathon Presentation Slides

This file contains the complete, slide-by-slide presentation content populated specifically for your solution and matching the provided template.

---

## Slide 1: Title Slide
### **AI-Powered Candidate Discovery & Ranking System**
- **Team Name**: Sairamparasa
- **Team Leader Name**: Sairam Parasa
- **Problem Statement**: Standard recruiting systems suffer from keyword matching limitations, which let keyword-stuffer traps and honeypot profiles bypass filters, while missing genuinely qualified candidates who use different terminology. This system solves this by building a semantic, two-stage ranking pipeline with advanced profile validation and availability checks.

---

## Slide 2: Solution Overview
### **What is your proposed solution?**
- A **Two-Stage Hybrid Retrieval & Ranking Pipeline** that is offline-first, highly scalable, and handles 100,000 candidates in under 1.5 minutes on a local CPU.
- Integrates fast structural filtering (Stage 1) with deep local sentence embeddings (Stage 2) and availability-based recruiter heuristics (Stage 3).

### **What differentiates your approach from traditional candidate matching systems?**
- **Robust Honeypot & Trap Defense**: Centralized anomaly detector that identifies impossible job durations, signup/activity date conflicts, and skill duration padding to block fake profiles.
- **Title vs Keyword Stuffing Analysis**: Disqualifies candidates with unrelated job titles (e.g., Marketing/HR Managers) trying to pass as ML Engineers using stuffed keywords.
- **Availability-Aware Scoring**: Re-scores candidates based on actual platform activity, notice period length, and recruiter response rates.

---

## Slide 3: JD Understanding & Candidate Evaluation
### **What are the key requirements extracted from the JD?**
- **Target Role**: Principal / Senior ML/AI Engineer
- **Experience Target**: 5-9 years (ideally 6-8 years with product-company backgrounds)
- **Core Skills**: Embeddings, vector databases (Pinecone, FAISS, Weaviate, Milvus), Python, and ranking evaluation metrics (NDCG, MAP, MRR).
- **Location Hubs**: Noida or Pune preferred (other Indian tech cities acceptable; visa constraints outside India).

### **Which candidate signals are most important for determining relevance?**
- **Primary Technical Alignment**: Skill duration and proficiency, and Redrob skill assessment scores.
- **Platform Availability**: Recruiter response rate (greater availability gets higher weight), notice period (sub-30 days preferred), and profile active recency.
- **Location Modifier**: Location-based multiplier prioritizing Noida/Pune.

---

## Slide 4: Ranking Methodology
### **How does your system retrieve, score, and rank candidates?**
1. **Stage 1 (Retrieval)**: Scans 100,000 candidates. Discards honeypots and disqualified titles. Generates heuristic scores to retrieve the Top 1,500 candidates.
2. **Stage 2 (Embeddings)**: Computes local SentenceTransformer embeddings for the Top 1,500 and measures cosine similarity against the JD query.
3. **Stage 3 (Hybrid Scorer)**: Combines Heuristics (Title, Skills, Experience, Behavior) and Semantic similarity.
4. **Stage 4 (Deterministic Sorting)**: Sorts candidates by final score, resolving score ties deterministically by `candidate_id` ascending.

### **What models, algorithms, or heuristics are used?**
- **Model**: Local `all-MiniLM-L6-v2` Sentence-Transformer model (running offline with no external network calls).
- **Heuristic Weights**: Title Match (35%), Skill Match (20%), Experience Alignment (10%), Platform Behavior (10%), and Semantic Similarity (25%).

---

## Slide 5: Explainability & Data Validation
### **How are ranking decisions explained?**
- Uses a deterministic, hash-based Recruiter Reasoning Engine. Generates 1-2 sentence recruiter justifications that cite exact years of experience, specific matching skills (e.g. PyTorch, Pinecone), and availability signals.

### **How do you prevent hallucinations or unsupported justifications?**
- **Strict Data-Binding**: Excludes any external generation models. All statements are built programmatically from facts read directly from the candidate's JSON profile structure.

### **How does your solution handle inconsistent, low-quality, or suspicious profiles?**
- **Honeypot Filter**: Centralized checkers verify that listed job duration in months does not exceed the start/end calendar dates, and flags "Expert" proficiencies with 0 duration. Flagged profiles receive a score of `0.0`.

---

## Slide 6: End-to-End Workflow
### **JD Input to Ranked Candidate Output**
```text
[ Job Description ] ──> Extracted Offline Requirements (jd_requirements.json)
                              │
                              ▼
[ candidates.jsonl (100k) ] ──> Parser (Normalizes profiles)
                              │
                              ▼
[ Stage 1 Heuristics ] ──> Filters 7,548 Honeypots & Disqualified Titles (Retrieves Top 1500)
                              │
                              ▼
[ Stage 2 Embeddings ] ──> Local all-MiniLM-L6-v2 Vector Similarity
                              │
                              ▼
[ Stage 3 Scoring ] ──> Combines Heuristics + Semantic Similarity + Relocation Multipliers
                              │
                              ▼
[ Stage 4 Sorting ] ──> Deterministic Tie-Breaking & Recruiter Reasoning (Top 100)
                              │
                              ▼
[ team_submission.csv ] ──> Passed validate_submission.py Validator
```

---

## Slide 7: System Architecture
- **Ingestion Package (`backend/ingestion/`)**: Normalizes inputs and structures JD requirements.
- **Retrieval Package (`backend/retrieval/`)**: High-performance streaming scanner executing Stage 1 heuristic filtering.
- **Embeddings Package (`backend/embeddings/`)**: Offline HuggingFace sentence-transformers execution engine.
- **Ranking Package (`backend/ranking/`)**: Calculates hybrid scores and generates recruiter justifications.
- **Submission Package (`backend/submission/`)**: Handles file formatting and runs compliance validation.
- **Utils Package (`backend/utils/`)**: General date utilities and central anomaly detection checks.

---

## Slide 8: Results & Performance
### **What results or insights demonstrate ranking quality?**
- **Top Candidates**: Highly targeted Senior ML/AI Engineers (e.g., Rank 1 CAND_0018499 score 0.9475: 7.2 yrs experience, expert in Weaviate and Pinecone).
- **Honeypots**: **0% honeypot contamination** in the final Top 100.
- **Trap Defense**: Successfully filtered out all keyword-stuffed profiles from unrelated professions.

### **How does your solution meet the challenge's runtime and compute constraints?**
- **Time**: Runs in **~1.5 minutes**, far below the 5-minute constraint.
- **Memory**: CPU-only execution consuming < 2GB RAM.
- **Network**: **100% offline** (SentenceTransformer weights are cached locally in the repository).

---

## Slide 9: Technologies Used
### **What technologies and frameworks were selected and why?**
- **Python 3**: Core scripting, data processing, and validation.
- **PyTorch & HuggingFace Transformers**: High-performance local neural network inference on CPU.
- **Sentence-Transformers (`all-MiniLM-L6-v2`)**: Compact, fast, and high-accuracy semantic representation model (384 dimensions).
- **Numpy**: Vectorized matrix operations for instant cosine similarity calculations.
- **Git**: Version control, with `.gitignore` set to prevent uploading large data files.

---

## Slide 10: Submission Assets
- **GitHub Repository**: [https://github.com/Sairamparasa/redrob-candidate-ranker](https://github.com/Sairamparasa/redrob-candidate-ranker) (Includes all source code, README, metadata, and local embedding weights).
- **Sandboxed hosted environment**: [https://huggingface.co/spaces/Sairamparasa/redrob-ranker](https://huggingface.co/spaces/Sairamparasa/redrob-ranker)
- **Shortlist Output**: `team_submission.csv` (100% compliant with `validate_submission.py` guidelines).
- **Metadata**: Pre-configured in `submission_metadata.yaml` for Stage 3 validation.
