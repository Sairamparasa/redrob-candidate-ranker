import os
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDINGS_MODEL_DIR

class LocalEmbedder:
    def __init__(self):
        print(f"Loading local SentenceTransformer model from '{EMBEDDINGS_MODEL_DIR}'...")
        if not os.path.exists(EMBEDDINGS_MODEL_DIR):
            raise FileNotFoundError(
                f"Local embedding model not found at '{EMBEDDINGS_MODEL_DIR}'. "
                "Please run download_model.py first."
            )
        self.model = SentenceTransformer(EMBEDDINGS_MODEL_DIR, local_files_only=True)
        print("Model loaded successfully.")

    def embed_texts(self, texts, batch_size=64, show_progress_bar=False):
        """
        Generates semantic embeddings for a list of texts using the local CPU-only model.
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,  # Normalized embeddings enable simple dot product for cosine similarity
            convert_to_numpy=True
        )
