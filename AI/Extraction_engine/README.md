# Extraction Engine — ScholarMind

## Overview

The **Extraction Engine** is a core component inside the `AI` module of ScholarMind.

Its purpose is to transform user queries into structured representations that can be used in:

- Ranking systems  
- Similarity matching  
- Vector databases  
- Retrieval pipelines (RAG)  
- Recruiting search workflows  

Over time, the extraction approach evolved from simple keyword extraction to semantic vector embeddings.

---

# Version History & Evolution

## 🔹 v1 — Keyword-Based Extraction

**File:** `v1.keyword_extractor.py`

### Approach

- Uses **KeyBERT**
- Extracts top-N keywords from user input
- Based on surface-level term matching

### Limitations

- Does not capture semantic meaning
- Misses contextual relationships
- Cannot detect instances or dependent concepts
- Not suitable for vector similarity systems

### Status

Kept for reference only  
Not recommended for recruiting search or ranking pipeline  

---

## 🔹 v2 — Semantic Query Embeddings (Initial Version)

**File:** `v2.Semantic_Query_Embeddings.py`

### Approach

- Uses **SPECTER model** (`allenai/specter`)
- Converts queries into 768-dimensional vectors
- Enables cosine similarity comparisons
- Introduces caching for performance

### Improvements Over v1

- Captures semantic meaning
- Understands contextual similarity
- Enables vector-based retrieval systems

---

## 🔹 v2 — Final Production Version (Updated)

**File:** `v2.Semantic_Query_Embeddings.py`  
*(This is the current and final version.)*

### Key Features

- Uses stable **SPECTER embedding model**
- Produces normalized 768-dimensional vectors
- Ready for cosine similarity search
- LRU caching (`maxsize=512`) for performance
- Safe input validation
- Clean production-ready implementation

### Why This Version Is Important

This version enables:

- Semantic understanding of queries
- Instance-level similarity detection
- Vector database compatibility
- Ranking & recruiting search improvements
- Stable integration into downstream AI pipelines

---



