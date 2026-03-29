from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str) -> List[float]:
    """
    Converts input text into a vector embedding.
    """
    embedding = model.encode(text, normalize_embeddings = True)
    return embedding.tolist()
