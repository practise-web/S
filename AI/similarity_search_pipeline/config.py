from pathlib import Path

class Settings():
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50
    EMBEDDING_MODEL: str = "cohere"
    VECTOR_DB: str = "chroma"
    COLLECTION_NAME: str = "documents"
    VECTOR_DB_PATH= Path("data/vector_db.faiss")
    K_BEST_RESULT = 5

    class Config:
        env_file = "app.env"

settings = Settings()
