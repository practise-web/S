#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScholarMind — Semantic Query Embedding (SPECTER)
------------------------------------------------
This module provides a production-ready function for computing
semantic embeddings of user queries using the SPECTER model.

Features:
- Converts queries to vector embeddings
- Caches results for repeated queries (improves performance)
- Ready for cosine similarity search in RAG pipelines
"""

from sentence_transformers import SentenceTransformer
from functools import lru_cache
import time

# -----------------------------
# Load SPECTER Model Once
# -----------------------------
embedding_model = SentenceTransformer("sentence-transformers/allenai-specter")


# -----------------------------
# Cached Query Embedding Function
# -----------------------------
@lru_cache(maxsize=200)
def embed_query(query: str):
    """
    Embed a text query using the SPECTER model (cached).

    Parameters
    ----------
    query : str
        The natural-language query to embed.

    Returns
    -------
    list or None
        The embedding vector as a Python list, or None if encoding fails.
    """
    start_time = time.time()

    try:
        vector = embedding_model.encode(query).tolist()
        latency = round((time.time() - start_time) * 1000, 2)
        print(f"Query embedded successfully | Latency: {latency} ms")
        return vector

    except Exception as e:
        print(f"Embedding failed: {e}")
        return None


# Local test
if __name__ == "__main__":
    query = "CRISPR gene editing in humans"
    vector = embed_query(query)

    print(f"Embedding vector length: {len(vector) if vector else 0}")
