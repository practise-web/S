# =========================================
# ScholarMind — Keyword Extraction Utility
# Using KeyBERT for Simple Keyword Extraction
# =========================================

from keybert import KeyBERT

# Load KeyBERT model once globally for efficiency
kw_model = KeyBERT(model="all-MiniLM-L6-v2")


def extract_keywords(text: str, top_n: int = 5):
    """
    Extract and rank the most relevant keywords from input text using KeyBERT.

    Parameters
    ----------
    text : str
        The text from which keywords will be extracted.
    top_n : int, optional
        Number of top keyword candidates to return (default = 5).

    Returns
    -------
    list of dict
        A list of dictionaries, each containing:
        - "keyword": extracted keyword or phrase
        - "score": relevance score (float)
    """
    # Generate diverse keyphrases (1–3 words)
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        use_mmr=True,
        diversity=0.7,
        top_n=top_n,
    )

    # Convert result to JSON-ready structure
    return [{"keyword": kw, "score": float(score)} for kw, score in keywords]


# Local test
if __name__ == "__main__":
    text_input = "How can artificial intelligence improve medical diagnosis and data analysis?"
    print("\n🔍 Extracting keywords...\n")

    output = extract_keywords(text_input, top_n=7)
    for item in output:
        print(f"• {item['keyword']:<30} ({item['score']:.2f})")
