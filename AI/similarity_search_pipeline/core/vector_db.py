from langchain_community.vectorstores import FAISS
from pathlib import Path
import logging

class VectorDB:
    def __init__(self, embedding_model, persist_path: str | None = None):
        self.embedding_model = embedding_model
        self.persist_path = persist_path

    def create(self, initial_chunks):
        """Create a new vector DB from initial chunks."""
        vector_db = FAISS.from_documents(initial_chunks, self.embedding_model)
        if self.persist_path:
            self.save(vector_db)
        return vector_db

    def add_docs(self, vector_db, new_chunks):
        """Add new chunks to an existing vector DB and optionally save."""
        vector_db.add_documents(new_chunks)
        if self.persist_path:
            self.save(vector_db)
        return vector_db

    def save(self, vector_db):
        """Save the vector DB to disk."""
        if not self.persist_path:
            logging.warning("No persist_path set. Vector DB not saved.")
            return
        path = Path(self.persist_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        vector_db.save_local(self.persist_path)
        logging.info(f"Vector DB saved at: {self.persist_path}")

    def load(self):
        """Load the vector DB from disk."""
        if not self.persist_path or not Path(self.persist_path).exists():
            logging.warning("Vector DB file does not exist.")
            return None
        logging.info(f"Loading vector DB from: {self.persist_path}")
        return FAISS.load_local(
            self.persist_path,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )