import argparse
import os
import sys
import numpy as np

# Ensure Python knows where to find the backend modules
# Since python might start in other folders, we change directory to the script's folder
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from backend.config import WEIGHT_SEMANTIC
from backend.embeddings.embeddings import LocalEmbedder
from backend.ranking.reasoning import generate_reasoning
from backend.prompts.prompts import JD_QUERY
from backend.retrieval.retriever import retrieve_top_candidates
from backend.submission.generator import generate_submission_file

def parse_args():
    parser = argparse.ArgumentParser(description="Rank candidates for the Redrob Hackathon.")
    parser.add_argument(
        "--candidates",
        type=str,
        default="./candidates.jsonl",
        help="Path to the candidates.jsonl file."
    )
    parser.add_argument(
        "--out",
        type=str,
        default="./submission.csv",
        help="Path to save the output submission.csv."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Resolve paths
    candidates_path = os.path.abspath(args.candidates)
    out_path = os.path.abspath(args.out)
    
    print(f"Reading candidates from: {candidates_path}")
    print(f"Output will be saved to: {out_path}")
    
    if not os.path.exists(candidates_path):
        print(f"Error: Candidate file not found at '{candidates_path}'")
        sys.exit(1)
        
    # 2. Stage 1: Fast Heuristic Retrieval (filtering honeypots and noise)
    print("Running Stage 1: Fast Heuristic Retrieval...")
    retrieved_candidates = retrieve_top_candidates(candidates_path)
    
    # 3. Stage 2: Semantic Embeddings
    print("Running Stage 2: Semantic Embeddings...")
    embedder = LocalEmbedder()
    jd_query = JD_QUERY
    query_emb = embedder.embed_texts([jd_query])[0]
    
    candidate_texts = [c["embed_text"] for c in retrieved_candidates]
    candidate_embs = embedder.embed_texts(candidate_texts, show_progress_bar=True)
    
    # Calculate cosine similarity (dot product of normalized embeddings)
    similarities = np.dot(candidate_embs, query_emb)
    
    # 4. Stage 3: Hybrid Scoring
    print("Running Stage 3: Hybrid Scoring...")
    final_list = []
    for i, candidate in enumerate(retrieved_candidates):
        sim = float(similarities[i])
        # Map cosine similarity from [-1, 1] to [0, 1]
        sim_normalized = max(0.0, (sim + 1.0) / 2.0)
        
        # Calculate final hybrid score
        h_score = candidate["heuristic_score"]
        final_score = h_score + sim_normalized * WEIGHT_SEMANTIC
        
        # Cap and round score between 0.0 and 1.0
        final_score = min(1.0, max(0.0, final_score))
        
        candidate["final_score"] = round(final_score, 4)
        candidate["semantic_similarity"] = sim_normalized
        final_list.append(candidate)
        
    # 5. Stage 4: Final Sorting and Ranking
    # Primary sort: final_score descending
    # Secondary sort (tie-breaker): candidate_id ascending
    final_list.sort(key=lambda x: (-x["final_score"], x["candidate_id"]))
    
    # Select Top 100
    top_100 = final_list[:100]
    
    # Format and generate reasoning
    formatted_rows = []
    for idx, candidate in enumerate(top_100):
        rank = idx + 1
        reasoning = generate_reasoning(candidate, rank)
        
        if rank <= 5:
            print(f"Rank {rank}: {candidate['candidate_id']} - Score: {candidate['final_score']:.4f} - {reasoning}")
            
        formatted_rows.append({
            "candidate_id": candidate["candidate_id"],
            "rank": rank,
            "score": candidate["final_score"],
            "reasoning": reasoning
        })
        
    # 6. Generate submission and validate
    generate_submission_file(formatted_rows, out_path, script_dir)

if __name__ == "__main__":
    main()
