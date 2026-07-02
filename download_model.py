import os
from sentence_transformers import SentenceTransformer

def main():
    os.chdir(r"c:\Users\saira\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge")
    model_name = "all-MiniLM-L6-v2"
    save_path = os.path.join("backend", "embeddings", model_name)
    print(f"Downloading model '{model_name}' and saving to '{save_path}'...")
    
    # Download and save
    model = SentenceTransformer(model_name)
    model.save(save_path)
    print("Model downloaded and saved successfully!")

if __name__ == "__main__":
    main()
