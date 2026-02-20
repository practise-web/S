#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScholarMind — Semantic Query Embedding (SPECTER)
------------------------------------------------

Features:
- Uses SPECTER (`allenai/specter`) for stable citation-aware embeddings
- Normalized embeddings for cosine similarity
- Cached results for repeated queries
- Safe input validation
"""

from sentence_transformers import SentenceTransformer
from functools import lru_cache
from typing import Optional
import numpy as np

# -----------------------------
# Load Model Once (Global)
# -----------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/allenai-specter"

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# -----------------------------
# Cached Query Embedding
# -----------------------------
@lru_cache(maxsize=512)
def embed_query(query: str) -> Optional[np.ndarray]:
    """
    Convert a user query into a normalized semantic embedding.

    Parameters
    ----------
    query : str
        Natural language user query.

    Returns
    -------
    np.ndarray | None
        Normalized embedding vector (768-dim),
        or None if input is invalid or encoding fails.
    """

    if not isinstance(query, str):
        return None

    query = query.strip()
    if not query:
        return None

    try:
        embedding = embedding_model.encode(query, normalize_embeddings=True)
        return embedding

    except Exception:
        return None


# -----------------------------
# Local Test 
# -----------------------------
if __name__ == "__main__":
    q = "CRISPR gene editing in humans"
    vec = embed_query(q)

    if vec is not None:
        print("Embedding OK")
        print("Vector shape:", vec.shape)
    else:
        print("Embedding failed")
