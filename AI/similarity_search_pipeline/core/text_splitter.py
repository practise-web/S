from config import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(pages:list[str]) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=settings.CHUNK_SIZE,
        length_function=len,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    documents = []
    metadatas = []
    for page in pages:
        documents.append(page.page_content)
        metadatas.append(page.metadata)

    chunks = text_splitter.create_documents(documents, metadatas)
    return chunks