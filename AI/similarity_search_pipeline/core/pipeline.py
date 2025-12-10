from core.pdf_parser import parsePDF
from core.text_splitter import split_text
from core.vector_db import VectorDB
from core.embedding import get_embedding_model
from config import settings
import logging

class SemanticSearchPipeline:
    def __init__(self):
        self.embedding_model = get_embedding_model(settings.EMBEDDING_MODEL)
        self.vector_manager = VectorDB(embedding_model=self.embedding_model, persist_path=str(settings.VECTOR_DB_PATH))
        self.vector_db = self.vector_manager.load()
    
    def add_pdf(self, pdf_path: str):
        # step 1
        raw_text = parsePDF(pdf_path)
        # step 2
        chunks = split_text(raw_text)
        # step 3
        if self.vector_db:
            self.vector_db = self.vector_manager.add_docs(self.vector_db, chunks)
        else:
            self.vector_db = self.vector_manager.create(chunks)
        
    def search(self, query:str, k: int = settings.K_BEST_RESULT):
        if not self.vector_db:
            logging.info("Vector DB is empty. Add PDFs first")
            return []
        return self.vector_db.similarity_search(query, k)